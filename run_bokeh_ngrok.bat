
@echo off
:: Start Bokeh server
start cmd /k "bokeh serve bokeh_visualization_deploy.py --allow-websocket-origin=*.ngrok-free.app"

:: Delay to make sure Bokeh starts before ngrok
timeout /t 5

:: Start ngrok to tunnel port 5006
start cmd /k "ngrok http 5006"
