library(shiny)

ui <- fluidPage(
  titlePanel("Mobility flows to/from malaria cases"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput(
        "case_id",
        label   = "Select case ID",
        choices = case_choices,
        selected = case_choices[1]
      ),
      helpText(
        "Left: incoming flows (prev + current month cases shown).",
        "Right: outgoing flows (current + next month cases shown).",
        "Only flows where both origin and destination elevation < 1000 m are shown."
      )
    ),
    
    mainPanel(
      fluidRow(
        column(
          width = 6,
          h4("Incoming travel"),
          leafletOutput("incoming_map", height = "500px")
        ),
        column(
          width = 6,
          h4("Outgoing travel"),
          leafletOutput("outgoing_map", height = "500px")
        )
      )
    )
  )
)
