#!/bin/bash
bokeh serve bokeh_visualization_with_tab.py --allow-websocket-origin=bokeh-visualization-dashboard.onrender.com --port $PORT
