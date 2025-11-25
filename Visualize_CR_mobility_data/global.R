## --- Created earlier in Datap prep for shiny app.RMD: ----------
library(shiny)
library(sf)
library(dplyr)
library(lubridate)
library(leaflet)   # ← this is the one you need for leafletOutput()
library(plotly)
library(ggplot2)
shiny_data <- readRDS("Data/shiny_mobility_data.rds")
districts_base <- shiny_data$districts_base        # still available if you need later
cases_all      <- shiny_data$cases_all
#flows_in_all   <- shiny_data$flows_in_all
#flows_out_all  <- shiny_data$flows_out_all
tiles_base     <- shiny_data$tiles_base   
travel_df_week <- shiny_data$travel_df_week

case_choices <- sort(unique(cases_all$case_id))
