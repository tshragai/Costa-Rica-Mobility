# ---- server.R (robust & simple full re-render) ----
library(shiny)
library(dplyr)
library(sf)
library(mapdeck)

shinyServer(function(input, output, session) {
  
  # ----------------- helpers -----------------
  prep_tiles_for_mapdeck <- function(x, id_col = "tile_id", max_rows = 200000) {
    if (is.null(x) || !inherits(x, "sf") || !"geometry" %in% names(x)) return(NULL)
    
    # strip Z/M, fix, drop empties
    x <- suppressWarnings(sf::st_zm(x, drop = TRUE, what = "ZM"))
    x <- suppressWarnings(sf::st_make_valid(x))
    x <- x[!sf::st_is_empty(x), , drop = FALSE]
    if (!nrow(x)) return(NULL)
    
    # polygons only, cast consistently
    g <- sf::st_geometry_type(x, by_geometry = TRUE)
    x <- x[g %in% c("POLYGON","MULTIPOLYGON"), , drop = FALSE]
    if (!nrow(x)) return(NULL)
    x <- suppressWarnings(sf::st_cast(x, "MULTIPOLYGON"))
    
    # reliable id: character, unique, non-NA
    if (!(id_col %in% names(x))) x[[id_col]] <- seq_len(nrow(x))
    x[[id_col]] <- as.character(x[[id_col]])
    nas <- is.na(x[[id_col]])
    if (any(nas)) x[[id_col]][nas] <- paste0("id_", which(nas))
    if (anyDuplicated(x[[id_col]]) > 0) x[[id_col]] <- make.unique(x[[id_col]])
    
    # keep size sane
    if (nrow(x) > max_rows) x <- x[sample.int(nrow(x), max_rows), , drop = FALSE]
    
    x
  }
  
  clean_arcs <- function(df, cap = 30000) {
    need <- c("Lon.home","Lat.home","Lon","Lat","o_tile_id","d_tile_id")
    if (is.null(df) || !all(need %in% names(df))) return(NULL)
    
    df <- df %>%
      mutate(
        Lon.home  = as.numeric(Lon.home),
        Lat.home  = as.numeric(Lat.home),
        Lon       = as.numeric(Lon),
        Lat       = as.numeric(Lat),
        o_tile_id = as.character(o_tile_id),
        d_tile_id = as.character(d_tile_id)
      ) %>%
      filter(is.finite(Lon.home), is.finite(Lat.home),
             is.finite(Lon),      is.finite(Lat))
    
    if (!nrow(df)) return(NULL)
    if (nrow(df) > cap) df <- df[sample.int(nrow(df), cap), , drop = FALSE]
    df
  }
  
  # ----------------- data reactives -----------------
  dat <- reactive({
    req(input$direction, input$district)
    build_flow_and_tiles(direction = input$direction, target_name = input$district)
  })
  
  tiles_r <- reactive({
    v <- dat(); req(v)
    prep_tiles_for_mapdeck(v$tiles_fill, id_col = "tile_id")
  })
  
  arcs_r <- reactive({
    v <- dat(); req(v)
    clean_arcs(v$loc_df)
  })
  
  # ----------------- click state -----------------
  clicked_tile <- reactiveVal(NULL)
  
  # store the last clicked tile_id (character)
  observeEvent(input$map_focal_tiles_click, {
    evt  <- input$map_focal_tiles_click
    tid  <- evt$id
    if (is.null(tid) && !is.null(evt$properties$tile_id)) tid <- evt$properties$tile_id
    if (!is.null(tid)) clicked_tile(as.character(tid))
  }, ignoreInit = TRUE)
  
  # reset click state when district or direction changes
  observeEvent(list(input$direction, input$district), {
    clicked_tile(NULL)
  }, ignoreInit = TRUE)
  
  # arcs to display: all arcs initially; if tile selected, filter by direction
  arcs_display <- reactive({
    arcs <- arcs_r(); req(arcs)
    tid  <- clicked_tile()
    if (is.null(tid)) return(arcs)
    if (identical(input$direction, "Incoming")) {
      dplyr::filter(arcs, d_tile_id == tid)
    } else {
      dplyr::filter(arcs, o_tile_id == tid)
    }
  })
  
  # ----------------- map render (full re-render) -----------------
  output$map <- renderMapdeck({
    req(input$direction, input$district)
    
    tiles  <- tiles_r()
    arcs   <- arcs_display()
    
    # bbox / center fallback
    if (!exists("bbox_cr")) {
      validate(need(exists("districts_ll"), "districts_ll not found; did global.R load?"))
      bbox_cr <<- sf::st_bbox(districts_ll)
    }
    cx <- mean(as.numeric(bbox_cr[c("xmin","xmax")]))
    cy <- mean(as.numeric(bbox_cr[c("ymin","ymax")]))
    
    # stable, tokenless basemap
    m <- mapdeck(
      style    = "https://demotiles.maplibre.org/style.json",
      location = c(cx, cy),
      zoom     = 6,
      pitch    = if (!is.null(input$pitch)) input$pitch else 45
    )
    
    # tiles: borders + flat fill, clickable; NO legends
    if (!is.null(tiles) && nrow(tiles) > 0) {
      m <- m %>% add_polygon(
        data             = tiles,
        layer_id         = "focal_tiles",
        id               = "tile_id",           # map click id
        stroke_colour    = "#666666",
        stroke_width     = 0.8,
        fill_colour      = "#88AACC",
        fill_opacity     = 0.35,
        legend           = FALSE,
        pickable         = TRUE,
        auto_highlight   = TRUE,
        highlight_colour = "#FFFFFF66"
      )
    }
    
    # arcs: fixed white; NO legends
    if (!is.null(arcs) && nrow(arcs) > 0 &&
        all(c("Lon.home","Lat.home","Lon","Lat") %in% names(arcs))) {
      arcs <- arcs %>%
        mutate(
          Lon.home = as.numeric(Lon.home),
          Lat.home = as.numeric(Lat.home),
          Lon      = as.numeric(Lon),
          Lat      = as.numeric(Lat)
        ) %>%
        filter(is.finite(Lon.home), is.finite(Lat.home),
               is.finite(Lon),      is.finite(Lat))
      
      if (nrow(arcs) > 0) {
        m <- m %>% add_arc(
          data         = arcs,
          layer_id     = "arc_layer",
          origin       = c("Lon.home","Lat.home"),
          destination  = c("Lon","Lat"),
          stroke_from  = "#FFFFFF",
          stroke_to    = "#FFFFFF",
          stroke_width = 2,
          brush_radius = 610,
          legend       = FALSE
        )
      }
    }
    
    m
  })
})
