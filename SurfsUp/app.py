# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"/api/v1.0/test<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature data for the last year"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).\
                filter(Measurement.station == 'USC00519281').all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return TMIN, TAVG, and TMAX for dates between the start and end date inclusive"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/test")
def temp_summary_start(start):
    # Convert start date string to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    # Query temperature summary statistics for start date and later
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for min_temp, avg_temp, max_temp in temp_stats:
        tobs_dict = {}
        tobs_dict["Minimum Temperature"] = min_temp
        tobs_dict["Average Temperature"] = avg_temp
        tobs_dict["Maximum Temperature"] = max_temp
        all_tobs.append(tobs_dict)
        
    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)
