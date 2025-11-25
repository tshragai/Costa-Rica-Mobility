server <- function(input, output, session) {
  
  ## ---- 0. Precompute / setup ----------------------------------------
  
  # Local copy with Date symptom_onset
  cases_all_local <- cases_all %>%
    dplyr::mutate(symptom_onset = as.Date(symptom_onset))
  
  # Shared base map (draw once)
  base_map <- leaflet::leaflet(options = leaflet::leafletOptions(preferCanvas = TRUE)) %>%
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
  
  
  ## ---- 0a. Base maps: draw once -------------------------------------
  
  # COMMENT OUT OLD MAPS ───────────────────────────────────────────────
  # output$incoming_map  <- leaflet::renderLeaflet({ base_map })
  # output$outgoing_map  <- leaflet::renderLeaflet({ base_map })
  
  # Only keep the weekly map
  output$case_week_map <- leaflet::renderLeaflet({ base_map })
  
  
  ## ---- 0b. Initialize dateInput range for cases-over-time tab -------
  
  observe({
    req(nrow(cases_all_local) > 0)
    
    onset_dates <- cases_all_local$symptom_onset
    onset_dates <- onset_dates[!is.na(onset_dates)]
    if (length(onset_dates) == 0) return()
    
    shiny::updateDateInput(
      session,
      "case_week_date",
      min   = min(onset_dates),
      max   = max(onset_dates),
      value = min(onset_dates)
    )
  })
  
  
  ## ---- 1. COMMENT OUT ALL FIRST-TAB LOGIC ---------------------------
  
  # selected_case <- reactive({ ... })
  # incoming_flows_case <- reactive({ ... })
  # outgoing_flows_case <- reactive({ ... })
  # incoming_cases_window <- reactive({ ... })
  # outgoing_cases_window <- reactive({ ... })
  
  # observeEvent(input$case_id, { ... })   # ENTIRE FIRST TAB REMOVED
  
  
  ## ---- 2. Cases-over-time map (tab 2) -------------------------------
  ## Uses precomputed travel_df_week (outgoing only) -------------------
  
  observeEvent(input$case_week_date, {
    req(input$case_week_date)
    
    idx_start <- as.Date(input$case_week_date)
    idx_end   <- idx_start + 6  # 7-day window
    
    # Cases during the selected week (yellow)
    cases_week <- cases_all_local %>%
      dplyr::filter(
        !is.na(symptom_onset),
        symptom_onset >= idx_start,
        symptom_onset <= idx_end
      )
    
    # Cases in the following two weeks (orange)
    cases_after <- cases_all_local %>%
      dplyr::filter(
        !is.na(symptom_onset),
        symptom_onset > idx_end,
        symptom_onset <= idx_end + 14
      )
    
    # Match to precomputed week
    week_start_sel <- lubridate::floor_date(idx_start, unit = "week")
    
    travel_week <- travel_df_week %>%
      dplyr::filter(week_start == week_start_sel)
    
    travel_tiles_week <- tiles_base %>%
      dplyr::left_join(travel_week, by = "tile_id")
    
    if (!"people" %in% names(travel_tiles_week)) {
      travel_tiles_week$people <- NA_real_
    }
    
    dom_travel_week <- travel_tiles_week$people
    if (all(is.na(dom_travel_week))) dom_travel_week <- c(0, 1)
    
    leaflet::leafletProxy("case_week_map") %>%
      leaflet::clearGroup("travel_tiles") %>%
      leaflet::clearGroup("cases_week") %>%
      leaflet::clearGroup("cases_after") %>%
      
      # Travel tiles
      leaflet::addPolygons(
        data        = travel_tiles_week,
        color       = "grey60",
        weight      = 0.2,
        opacity     = 0.4,
        fill        = TRUE,
        fillColor = ~ifelse(
          is.na(people) | people < 0.4,
          "transparent",
          colorNumeric("Reds", log1p(dom_travel_week))(log1p(people))
        ),
        fillOpacity = ~ifelse(
          is.na(people) | people < 0.4,
          0.0,
          0.9
        ),
        group       = "travel_tiles",
        label       = ~paste0(
          "Tile: ", tile_id,
          "<br>Total travellers (week+2): ",
          ifelse(is.na(people), 0, round(people, 1))
        )
      ) %>%
      
      # Week cases (yellow)
      {
        if (nrow(cases_week) > 0)
          leaflet::addCircleMarkers(.,
                                    data        = cases_week,
                                    radius      = 6,
                                    stroke      = TRUE,
                                    weight      = 1,
                                    color       = "black",
                                    fillColor   = "yellow",
                                    fillOpacity = 1,
                                    group       = "cases_week",
                                    label       = ~paste0("Onset: ", symptom_onset),
                                    popup       = ~paste0("<strong>ID:</strong> ", case_id,
                                                          "<br><strong>Onset:</strong> ", symptom_onset)
          )
        else .
      } %>%
      
      # Following 2 weeks (orange)
      {
        if (nrow(cases_after) > 0)
          leaflet::addCircleMarkers(.,
                                    data        = cases_after,
                                    radius      = 5,
                                    stroke      = TRUE,
                                    weight      = 1,
                                    color       = "black",
                                    fillColor   = "orange",
                                    fillOpacity = 0.8,
                                    group       = "cases_after",
                                    label       = ~paste0("Onset: ", symptom_onset),
                                    popup       = ~paste0("<strong>ID:</strong> ", case_id,
                                                          "<br><strong>Onset:</strong> ", symptom_onset)
          )
        else .
      }
  })
  
}
