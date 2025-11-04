# ---- global.R ----

# Set libraries
library(shiny)
library(sf)
library(dplyr)
library(stringi)
library(scales)
library(mapdeck)
library(viridisLite)

# Set Mapdeck token
  mapdeck::set_token("pk.eyJ1IjoidHNocmFnYWkiLCJhIjoiY21oam84d2JtMWRnOTJpcTY0Mm9uamVmaCJ9.G1P5tS1f60KuJBKTkM-9lQ")

# Read in necessary data
  setwd("~/Costa-Rica-Mobility/Data")
  pop_tiles <- st_read("costa_rica_activity_tiles_population.geojson")  
  ca_aug <- read.csv("ca_aug.csv")
  districts<- st_read("Costa_Rica_districts.gpkg")

# 2) Config
name_col  <- "NOMB_UGED"  # district name field in your shapefile
norm_str  <- function(x) stri_trans_general(x, "Latin-ASCII") |> toupper() |> trimws()

# Ensure lon/lat CRS for map overlays
districts_ll <- st_transform(districts, 4326) |> st_make_valid()
pop_tiles_ll <- st_transform(pop_tiles, 4326)
bbox_cr      <- st_bbox(districts_ll)

# Ensure ca_aug has weight
if (!"weight" %in% names(ca_aug)) {
  ca_aug <- ca_aug %>% mutate(weight = visit_fraction * origin_pop)
}

# If origin/dest district columns are missing, attach them (no summarizing)
if (!all(c("origin_district","dest_district") %in% names(ca_aug))) {
  origins_sf <- st_as_sf(ca_aug, coords = c("home_longitude","home_latitude"),
                         crs = 4326, remove = FALSE)
  dests_sf   <- st_as_sf(ca_aug, coords = c("visit_longitude","visit_latitude"),
                         crs = 4326, remove = FALSE)
  o_join <- st_join(origins_sf, districts_ll[, name_col], left = TRUE) |>
    st_drop_geometry() |> transmute(origin_district = .data[[name_col]])
  d_join <- st_join(dests_sf, districts_ll[, name_col], left = TRUE) |>
    st_drop_geometry() |> transmute(dest_district   = .data[[name_col]])
  ca_aug <- bind_cols(ca_aug, o_join, d_join)
}

# Tile centroids for arc endpoints
tile_centroids <- pop_tiles_ll |>
  st_centroid() |>
  transmute(tile_id,
            Lon = st_coordinates(geometry)[,1],
            Lat = st_coordinates(geometry)[,2]) |>
  st_drop_geometry()

# Backdrop layers (fill + outlines)
districts_fill  <- districts_ll |> mutate(fill_hex = "#EAEAEA")
districts_lines <- districts_ll |>
  st_boundary() |>
  st_cast("MULTILINESTRING") |>
  st_as_sf() |>
  mutate(stroke_hex = "#555555")

# Helper: build flows & tiles per selection
build_flow_and_tiles <- function(direction = c("Incoming","Outgoing"),
                                 target_name) {
  direction <- match.arg(direction)
  target_norm <- norm_str(target_name)
  
  if (direction == "Incoming") {
    flows <- ca_aug %>%
      mutate(dest_norm = norm_str(dest_district)) %>%
      filter(dest_norm == target_norm,
             !is.na(o_tile_id), !is.na(d_tile_id)) %>%
      group_by(o_tile_id, d_tile_id) %>%
      summarise(weight = sum(weight, na.rm = TRUE), .groups = "drop")
    
    tiles_in_target <- st_intersection(pop_tiles_ll, 
                                       districts_ll %>% filter(norm_str(.data[[name_col]]) == target_norm)) %>%
      select(tile_id)
    
    tile_weights <- flows %>%
      group_by(d_tile_id) %>%
      summarise(value = sum(weight, na.rm = TRUE), .groups = "drop")
    
    tiles_fill <- tiles_in_target %>%
      left_join(tile_weights, by = c("tile_id" = "d_tile_id")) %>%
      mutate(value = ifelse(is.na(value), 0, value))
  } else {
    flows <- ca_aug %>%
      mutate(origin_norm = norm_str(origin_district)) %>%
      filter(origin_norm == target_norm,
             !is.na(o_tile_id), !is.na(d_tile_id)) %>%
      group_by(o_tile_id, d_tile_id) %>%
      summarise(weight = sum(weight, na.rm = TRUE), .groups = "drop")
    
    tiles_in_target <- st_intersection(pop_tiles_ll, 
                                       districts_ll %>% filter(norm_str(.data[[name_col]]) == target_norm)) %>%
      select(tile_id)
    
    tile_weights <- flows %>%
      group_by(o_tile_id) %>%
      summarise(value = sum(weight, na.rm = TRUE), .groups = "drop")
    
    tiles_fill <- tiles_in_target %>%
      left_join(tile_weights, by = c("tile_id" = "o_tile_id")) %>%
      mutate(value = ifelse(is.na(value), 0, value))
  }
  
  # Arc dataframe for mapdeck::add_arc (no geometry needed)
  loc.df <- flows %>%
    left_join(tile_centroids %>% rename(o_tile_id = tile_id,
                                        Lon.home = Lon, Lat.home = Lat),
              by = "o_tile_id") %>%
    left_join(tile_centroids %>% rename(d_tile_id = tile_id,
                                        Lon = Lon, Lat = Lat),
              by = "d_tile_id") %>%
    filter(is.finite(Lon.home), is.finite(Lat.home),
           is.finite(Lon), is.finite(Lat),
           o_tile_id != d_tile_id) %>%
    mutate(
      w_log    = log1p(weight),
      stroke_w = rescale(w_log, to = c(1, 8), from = range(w_log, na.rm = TRUE)),
      color    = viridis(100)[as.integer(rescale(w_log, to = c(1, 100)))],
      tooltip  = sprintf("OD tiles: %s → %s<br/>Weight: %.3f",
                         o_tile_id, d_tile_id, weight)
    )
  
  list(tiles_fill = tiles_fill, loc_df = loc.df)
}

# District choices for UI
district_choices <- sort(unique(districts_ll[[name_col]]))