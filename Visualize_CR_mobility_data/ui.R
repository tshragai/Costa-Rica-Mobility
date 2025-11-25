library(shiny)
library(leaflet)

ui <- fluidPage(
  
  titlePanel("Mobility flows to/from malaria cases"),
  
  # ──────────────────────────────────────────────────────────────
  # COMMENT OUT THE ORIGINAL SIDEBAR + FIRST TWO MAPS
  # ──────────────────────────────────────────────────────────────
  #
  # sidebarLayout(
  #   sidebarPanel(
  #     selectInput(
  #       "case_id",
  #       label   = "Select case ID",
  #       choices = case_choices,
  #       selected = case_choices[1]
  #     ),
  #     helpText(
  #       "Left: incoming flows (prev + current month cases shown).",
  #       "Right: outgoing flows (current + next month cases shown).",
  #       "Only flows where both origin and destination elevation < 1000 m are shown."
  #     )
  #   ),
  #
  #   mainPanel(
  #     fluidRow(
  #       column(
  #         width = 6,
  #         h4("Incoming travel"),
  #         leafletOutput("incoming_map", height = "500px")
  #       ),
  #       column(
  #         width = 6,
  #         h4("Outgoing travel"),
  #         leafletOutput("outgoing_map", height = "500px")
  #       )
  #     )
  #   )
  # )
  #
  # ──────────────────────────────────────────────────────────────
  # END COMMENTED SECTION
  # ──────────────────────────────────────────────────────────────
  
  
  # ──────────────────────────────────────────────────────────────
  # NEW: Only show the weekly travel map
  # ──────────────────────────────────────────────────────────────
  
  sidebarLayout(
    sidebarPanel(
      h4("Select week"),
      dateInput(
        "case_week_date",
        "Week start date:",
        value = Sys.Date(),
        format = "yyyy-mm-dd"
      ),
      helpText("Shows cases during selected week (yellow), 
               following 2 weeks (orange), 
               and outgoing travel specifically originating in tiles with a case (red shading).")
    ),
    
    mainPanel(
      h3("Cases over time + outgoing travel"),
      leafletOutput("case_week_map", height = "650px")
    )
  )
)

