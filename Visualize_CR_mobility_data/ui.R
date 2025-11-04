# ---- ui.R ----
library(shiny)
library(mapdeck)

shinyUI(
  fluidPage(
    titlePanel("Costa Rica Mobility — Flow Maps"),
    sidebarLayout(
      sidebarPanel(
        selectInput("basemap", "Basemap style",
                    choices = c("Mapbox - Streets"  = "mapbox://styles/mapbox/streets-v12",
                                "Mapbox - Outdoors" = "mapbox://styles/mapbox/outdoors-v12",
                                "Mapbox - Light"    = "mapbox://styles/mapbox/light-v11",
                                "MapLibre (no token)" = "https://demotiles.maplibre.org/style.json"),
                    selected = "mapbox://styles/mapbox/streets-v12"),
        selectInput("district", "Focal district", choices = district_choices),
        radioButtons("direction", "Direction", choices = c("Incoming","Outgoing"), inline = TRUE),
        sliderInput("pitch", "Map pitch (°)", min = 0, max = 60, value = 45, step = 5),
        sliderInput("qcut", "Hide flows below quantile", min = 0, max = 0.99, value = 0.00, step = 0.01),
        helpText("Tip: choose MapLibre if Mapbox tiles are blocked by your network.")
      ),
      mainPanel(
        mapdeckOutput("map", height = "680px"),
      )
    )
  )
)

