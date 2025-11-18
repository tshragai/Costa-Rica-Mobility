server <- function(input, output, session) {
  
  ## ---- 0. Base maps: draw once --------------------------------------
  
  output$incoming_map <- leaflet::renderLeaflet({
    leaflet::leaflet(options = leaflet::leafletOptions(preferCanvas = TRUE)) %>%
      leaflet::addTiles() %>%
      leaflet::addPolygons(
        data        = tiles_base,
        color       = "grey70",
        weight      = 0.3,
        opacity     = 0.6,
        fill        = TRUE,
        fillColor   = "grey90",
        fillOpacity = 0.4,
        group       = "tiles_base"
      ) %>%
      leaflet::setView(lng = -84, lat = 9.5, zoom = 7)
  })
  
  output$outgoing_map <- leaflet::renderLeaflet({
    leaflet::leaflet(options = leaflet::leafletOptions(preferCanvas = TRUE)) %>%
      leaflet::addTiles() %>%
      leaflet::addPolygons(
        data        = tiles_base,
        color       = "grey70",
        weight      = 0.3,
        opacity     = 0.6,
        fill        = TRUE,
        fillColor   = "grey90",
        fillOpacity = 0.4,
        group       = "tiles_base"
      ) %>%
      leaflet::setView(lng = -84, lat = 9.5, zoom = 7)
  })
  
  ## ---- 1. Reactives for data selection ------------------------------
  
  selected_case <- reactive({
    req(input$case_id)
    cases_all %>%
      dplyr::filter(as.character(case_id) == as.character(input$case_id))
  })
  
  incoming_flows_case <- reactive({
    req(input$case_id)
    flows_in_all %>%
      dplyr::filter(as.character(case_id) == as.character(input$case_id))
  })
  
  outgoing_flows_case <- reactive({
    req(input$case_id)
    flows_out_all %>%
      dplyr::filter(as.character(case_id) == as.character(input$case_id))
  })
  
  # All cases on or before the index case date (incoming panel)
  incoming_cases_window <- reactive({
    sel <- selected_case()
    if (nrow(sel) == 0 || !"symptom_onset" %in% names(sel)) {
      return(cases_all[0, ])
    }
    
    idx_date <- sel$symptom_onset[1]
    if (!inherits(idx_date, c("Date", "POSIXct", "POSIXt"))) {
      idx_date <- as.Date(idx_date)
    }
    if (is.na(idx_date)) {
      return(cases_all[0, ])
    }
    
    cases_all %>%
      dplyr::filter(
        !is.na(symptom_onset),
        symptom_onset <= idx_date
      )
  })
  
  # All cases on or after the index case date (outgoing panel)
  outgoing_cases_window <- reactive({
    sel <- selected_case()
    if (nrow(sel) == 0 || !"symptom_onset" %in% names(sel)) {
      return(cases_all[0, ])
    }
    
    idx_date <- sel$symptom_onset[1]
    if (!inherits(idx_date, c("Date", "POSIXct", "POSIXt"))) {
      idx_date <- as.Date(idx_date)
    }
    if (is.na(idx_date)) {
      return(cases_all[0, ])
    }
    
    cases_all %>%
      dplyr::filter(
        !is.na(symptom_onset),
        symptom_onset >= idx_date
      )
  })
  
  ## ---- 2. Map updates when case changes -----------------------------
  
  observeEvent(input$case_id, ignoreInit = FALSE, {
    
    case_sel      <- selected_case()
    flows_sf_in   <- incoming_flows_case()
    flows_sf_out  <- outgoing_flows_case()
    cases_win_in  <- incoming_cases_window()
    cases_win_out <- outgoing_cases_window()
    
    ## ---- 2a. Build tile data with pop_in / pop_out ------------------
    
    # Incoming: people_travel FROM each origin tile_o TO the case tile
    if (nrow(flows_sf_in) > 0) {
      pop_in_df <- flows_sf_in %>%
        sf::st_drop_geometry() %>%
        dplyr::group_by(tile_o) %>%
        dplyr::summarise(
          pop_in = sum(people_travel, na.rm = TRUE),
          .groups = "drop"
        )
      
      tiles_in <- tiles_base %>%
        dplyr::left_join(pop_in_df, by = c("tile_id" = "tile_o"))
    } else {
      tiles_in <- tiles_base %>%
        dplyr::mutate(pop_in = NA_real_)
    }
    
    # Outgoing: people_travel FROM the case tile TO each destination tile_d
    if (nrow(flows_sf_out) > 0) {
      pop_out_df <- flows_sf_out %>%
        sf::st_drop_geometry() %>%
        dplyr::group_by(tile_d) %>%
        dplyr::summarise(
          pop_out = sum(people_travel, na.rm = TRUE),
          .groups = "drop"
        )
      
      tiles_out <- tiles_base %>%
        dplyr::left_join(pop_out_df, by = c("tile_id" = "tile_d"))
    } else {
      tiles_out <- tiles_base %>%
        dplyr::mutate(pop_out = NA_real_)
    }
    
    # make sure columns exist
    if (!"pop_in"  %in% names(tiles_in))  tiles_in$pop_in   <- NA_real_
    if (!"pop_out" %in% names(tiles_out)) tiles_out$pop_out <- NA_real_
    
    # domains for color scales
    dom_in  <- tiles_in$pop_in
    if (all(is.na(dom_in)))  dom_in  <- c(0, 1)
    dom_out <- tiles_out$pop_out
    if (all(is.na(dom_out))) dom_out <- c(0, 1)
    
    pal_in  <- leaflet::colorNumeric("YlOrRd", domain = dom_in,  na.color = "transparent")
    pal_out <- leaflet::colorNumeric("Blues",  domain = dom_out, na.color = "transparent")
    
    ## ---- 2b. Incoming map (left) ------------------------------------
    leaflet::leafletProxy("incoming_map") %>%
      leaflet::clearGroup("tiles_case") %>%
      leaflet::clearGroup("flows") %>%
      leaflet::clearGroup("cases") %>%
      leaflet::clearGroup("case_sel") %>%
      
      # tiles colored by incoming population
      leaflet::addPolygons(
        data        = tiles_in,
        color       = "grey60",
        weight      = 0.2,
        opacity     = 0.4,
        fill        = TRUE,
        fillColor = ~ifelse(
          is.na(pop_in) | pop_in < .4,
          "transparent",
          colorNumeric(
            palette = "Reds",
            domain  = log1p(dom_in)
          )(log1p(pop_in))
        ),
        
        fillOpacity = ~ifelse(
          is.na(pop_in) | pop_in < 0.1,
          0.0,   # fully clear
          0.9    # strongly visible
        ),
        group       = "tiles_case",
        label       = ~paste0(
          "Tile: ", tile_id, "<br>",
          "Incoming people: ",
          ifelse(is.na(pop_in), 0, round(pop_in, 1))
        )
      ) %>%
      
      # incoming flows (blue) — COMMENTED OUT
      {
        # if (nrow(flows_sf_in) > 0)
        #   leaflet::addPolylines(.,
        #     data   = flows_sf_in,
        #     color  = "blue",
        #     weight = 1.5,
        #     opacity = 0.25,
        #     group  = "flows"
        #   )
        .
      } %>%
      
      # all previous/on-date cases (green instead of white)
      {
        if (nrow(cases_win_in) > 0)
          leaflet::addCircleMarkers(.,
                                    data   = cases_win_in,
                                    radius = 3,
                                    stroke = TRUE,
                                    weight = 0.5,
                                    color  = "black",
                                    fillColor = "#00FFFF",
                                    fillOpacity = 0.9,
                                    group  = "cases",
                                    popup  = ~paste("case_id:", case_id)
          )
        else .
      } %>%
      
      # selected case (yellow)
      {
        if (nrow(case_sel) > 0)
          leaflet::addCircleMarkers(.,
                                    data   = case_sel,
                                    radius = 8,
                                    stroke = TRUE,
                                    weight = 1,
                                    color  = "black",
                                    fillColor = "yellow",
                                    fillOpacity = 1,
                                    group  = "case_sel"
          )
        else .
      }
    
    
    ## ---- 2c. Outgoing map (right) -----------------------------------
    leaflet::leafletProxy("outgoing_map") %>%
      leaflet::clearGroup("tiles_case") %>%
      leaflet::clearGroup("flows") %>%
      leaflet::clearGroup("cases") %>%
      leaflet::clearGroup("case_sel") %>%
      
      # outgoing tiles
      leaflet::addPolygons(
        data        = tiles_out,
        color       = "transparent",
        weight      = 0.2,
        opacity     = 0.4,
        fill        = TRUE,
        fillColor = ~ifelse(
          is.na(pop_out) | pop_out < .4,
          NA,
          colorNumeric(
            palette = "Reds",
            domain  = log1p(dom_out)
          )(log1p(pop_out))
        ),
        fillOpacity = ~ifelse(
          is.na(pop_out) | pop_out < .4,
          0.0,
          0.9
        ),
        group       = "tiles_case",
        label       = ~paste0(
          "Tile: ", tile_id, "<br>",
          "Outgoing people: ",
          ifelse(is.na(pop_out), 0, round(pop_out, 1))
        )
      ) %>%
      
      # outgoing flows (red) — COMMENTED OUT
      {
        # if (nrow(flows_sf_out) > 0)
        #   leaflet::addPolylines(.,
        #     data   = flows_sf_out,
        #     color  = "red",
        #     weight = 1.5,
        #     opacity = 0.25,
        #     group  = "flows"
        #   )
        .
      } %>%
      
      # future/on-date cases (green)
      {
        if (nrow(cases_win_out) > 0)
          leaflet::addCircleMarkers(.,
                                    data   = cases_win_out,
                                    radius = 3,
                                    stroke = TRUE,
                                    weight = 0.5,
                                    color  = "black",
                                    fillColor = "#00FFFF",
                                    fillOpacity = 0.9,
                                    group  = "cases",
                                    popup  = ~paste("case_id:", case_id)
          )
        else .
      } %>%
      
      # selected case (yellow)
      {
        if (nrow(case_sel) > 0)
          leaflet::addCircleMarkers(.,
                                    data   = case_sel,
                                    radius = 8,
                                    stroke = TRUE,
                                    weight = 1,
                                    color  = "black",
                                    fillColor = "yellow",
                                    fillOpacity = 1,
                                    group  = "case_sel"
          )
        else .
      }
    
    
  })
  
}
