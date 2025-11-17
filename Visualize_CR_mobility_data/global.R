# global.R -------------------------------------------------------------
library(shiny)
library(sf)
library(dplyr)
library(lubridate)
library(leaflet)
library(plotly)
library(ggplot2)

## --- Created earlier in Datap prep for shiny app.RMD: ----------
setwd("~/Costa-Rica-Mobility")
shiny_data     <- readRDS("shiny_mobility_data.rds")
districts_base <- shiny_data$districts_base
cases_all      <- shiny_data$cases_all
flows_in_all   <- shiny_data$flows_in_all
flows_out_all  <- shiny_data$flows_out_all
case_choices <- sort(unique(cases_all$case_id))

