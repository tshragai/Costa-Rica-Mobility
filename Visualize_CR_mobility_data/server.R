server <- function(input, output, session) {
  
  ## ---- 0. Base maps: draw once --------------------------------------
  
  output$incoming_map <- leaflet::renderLeaflet({
    leaflet::leaflet(options = leaflet::leafletOptions(preferCanvas = TRUE)) %>%
      leaflet::addTiles() %>%
      leaflet::addPolygons(
        data   = districts_base,
        color  = "grey70",
        weight = 0.5,
        fill   = FALSE,
        opacity = 0.6,
        group  = "districts"
      ) %>%
      leaflet::setView(lng = -84, lat = 9.5, zoom = 7)
  })
  
  output$outgoing_map <- leaflet::renderLeaflet({
    leaflet::leaflet(options = leaflet::leafletOptions(preferCanvas = TRUE)) %>%
      leaflet::addTiles() %>%
      leaflet::addPolygons(
        data   = districts_base,
        color  = "grey70",
        weight = 0.5,
        fill   = FALSE,
        opacity = 0.6,
        group  = "districts"
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
    
    from_date <- lubridate::floor_date(idx_date %m-% months(1), unit = "month")
    to_date   <- lubridate::ceiling_date(idx_date, unit = "month") - lubridate::days(1)
    
    cases_all %>%
      dplyr::filter(
        symptom_onset >= from_date,
        symptom_onset <= to_date
      )
  })
  
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
    
    from_date <- lubridate::floor_date(idx_date, unit = "month")
    to_date   <- lubridate::ceiling_date(idx_date %m+% months(1), unit = "month") - lubridate::days(1)
    
    cases_all %>%
      dplyr::filter(
        symptom_onset >= from_date,
        symptom_onset <= to_date
      )
  })
  
  ## ---- 2. Lightweight map updates -----------------------------------
  
  observeEvent(input$case_id, ignoreInit = FALSE, {
    
    case_sel     <- selected_case()
    flows_sf_in  <- incoming_flows_case()
    flows_sf_out <- outgoing_flows_case()
    cases_win_in <- incoming_cases_window()
    cases_win_out<- outgoing_cases_window()
    
    ## Incoming map (left) ---------------------------------------------
    leaflet::leafletProxy("incoming_map") %>%
      leaflet::clearGroup("flows") %>%
      leaflet::clearGroup("cases") %>%
      leaflet::clearGroup("case_sel") %>%
      
      # incoming flows (blue)
      { if (nrow(flows_sf_in) > 0)
        leaflet::addPolylines(.,
                              data   = flows_sf_in,
                              color  = "blue",
                              weight = 1.5,
                              opacity = 0.25,
                              group  = "flows"
        )
        else . } %>%
      
      # previous + current month cases (white)
      { if (nrow(cases_win_in) > 0)
        leaflet::addCircleMarkers(.,
                                  data   = cases_win_in,
                                  radius = 3,
                                  stroke = TRUE,
                                  weight = 0.5,
                                  color  = "black",
                                  fillColor = "white",
                                  fillOpacity = 0.8,
                                  group  = "cases",
                                  popup  = ~paste("case_id:", case_id)
        )
        else . } %>%
      
      # selected case (yellow)
      { if (nrow(case_sel) > 0)
        leaflet::addCircleMarkers(.,
                                  data   = case_sel,
                                  radius = 6,
                                  stroke = TRUE,
                                  weight = 1,
                                  color  = "black",
                                  fillColor = "yellow",
                                  fillOpacity = 1,
                                  group  = "case_sel"
        )
        else . }
    
    ## Outgoing map (right) --------------------------------------------
    leaflet::leafletProxy("outgoing_map") %>%
      leaflet::clearGroup("flows") %>%
      leaflet::clearGroup("cases") %>%
      leaflet::clearGroup("case_sel") %>%
      
      # outgoing flows (red)
      { if (nrow(flows_sf_out) > 0)
        leaflet::addPolylines(.,
                              data   = flows_sf_out,
                              color  = "red",
                              weight = 1.5,
                              opacity = 0.25,
                              group  = "flows"
        )
        else . } %>%
      
      # current + next month cases (white)
      { if (nrow(cases_win_out) > 0)
        leaflet::addCircleMarkers(.,
                                  data   = cases_win_out,
                                  radius = 3,
                                  stroke = TRUE,
                                  weight = 0.5,
                                  color  = "black",
                                  fillColor = "white",
                                  fillOpacity = 0.8,
                                  group  = "cases",
                                  popup  = ~paste("case_id:", case_id)
        )
        else . } %>%
      
      # selected case (yellow)
      { if (nrow(case_sel) > 0)
        leaflet::addCircleMarkers(.,
                                  data   = case_sel,
                                  radius = 6,
                                  stroke = TRUE,
                                  weight = 1,
                                  color  = "black",
                                  fillColor = "yellow",
                                  fillOpacity = 1,
                                  group  = "case_sel"
        )
        else . }
    
  })
  
}
