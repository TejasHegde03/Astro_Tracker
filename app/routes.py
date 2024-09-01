from flask import render_template, send_from_directory, Blueprint, current_app, redirect, url_for, session , request
import requests
import os
import mysql.connector
from dotenv import load_dotenv


routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    observer_lat = 12.97623
    observer_lng = 77.60329
    observer_alt = 900
    search_radius = 45
    category_id = 0
    api_key = "HZ3NA9-KEXVFH-A6FGN4-57O3"
    
    url = f"https://api.n2yo.com/rest/v1/satellite/above/{observer_lat}/{observer_lng}/{observer_alt}/{search_radius}/{category_id}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()  
    return render_template('index.html', satellites=data.get('above', []))

@routes_bp.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'images'), filename)

@routes_bp.route('/about_us')
def about_us():
    return render_template('about_us.html')

@routes_bp.route('/potd')
def potd():
    return render_template('pic_of_the_day.html')

@routes_bp.route('/satellite-info/')
def satellite_info():
    try:
        with current_app.config['DB_CONNECTION'].cursor(dictionary=True) as cursor:

            cursor.execute('SELECT * FROM Satellite')
            satellites = cursor.fetchall()

            cursor.execute('SELECT * FROM Orbit_Details')
            orbit_details = cursor.fetchall()

            cursor.execute('SELECT * FROM Launch_Details')
            launch_details = cursor.fetchall()

            cursor.execute('SELECT * FROM Observer')
            observers = cursor.fetchall()

            cursor.execute('SELECT * FROM Obs_Coordinates')
            obs_coordinates = cursor.fetchall()

        satellites_with_details = []
        for satellite in satellites:
            satellite_observers = [observer for observer in observers if observer['Satellite_id'] == satellite['Satellite_id']]
            satellite_orbit = next((orbit for orbit in orbit_details if orbit['Satellite_id'] == satellite['Satellite_id']), None)
            satellite_launch_details = next((launch for launch in launch_details if launch['Launch_id'] == satellite['Launch_id']), None)

            satellite_coordinates = []
            for observer in satellite_observers:
                observer_id = observer['Observer_id']
                coordinates = next((coord for coord in obs_coordinates if coord['Observer_id'] == observer_id), None)
                if coordinates:
                    satellite_coordinates.append(coordinates)

            satellite['observers'] = satellite_observers
            satellite['orbit'] = satellite_orbit
            satellite['launch_details'] = satellite_launch_details
            satellite['coordinates'] = satellite_coordinates

            nord_id = satellite['nord_id']
            observer_lat = 12.97623 
            observer_lng = 77.60329  
            observer_alt = 900
            seconds = 1

            url = f"https://api.n2yo.com/rest/v1/satellite/positions/{nord_id}/{observer_lat}/{observer_lng}/{observer_alt}/{seconds}&apiKey=HZ3NA9-KEXVFH-A6FGN4-57O3"
            response = requests.get(url)
            data = response.json()

            if 'positions' in data:
                satellite['positions'] = data['positions']

            satellites_with_details.append(satellite)

        return render_template('satellite-info.html', launch_details=launch_details, satellites=satellites_with_details, obs_coordinates=obs_coordinates)
    
    except Exception as e:
        return f"An error occurred: {e}"
    

@routes_bp.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with current_app.config['DB_CONNECTION'].cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password))
                user = cursor.fetchone()
                
                if user:
                    session['loggedin'] = True
                    session['id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('routes.sidebar'))
                else:
                    error = 'Invalid username or password'
        
        except mysql.connector.Error as err:
            error = f"An error occurred: {err}"
    
    return render_template('login.html', error=error)

@routes_bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('login.html', error='Password does not match the Confirm Password')
        try:
            with current_app.config['DB_CONNECTION'].cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    return render_template('login.html', error='Username already exists')
                
            
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password))
                current_app.config['DB_CONNECTION'].commit()
                
            
                return redirect(url_for('routes.sidebar'))
        
        except mysql.connector.Error as err:
            return f"An error occurred: {err}"
    
    return render_template('login.html')

@routes_bp.route("/sidebar", methods=['GET'])
def sidebar():
    try:
        with current_app.config['DB_CONNECTION'].cursor(dictionary=True) as cursor:

            cursor.execute('SELECT * FROM Satellite')
            satellites = cursor.fetchall()

            cursor.execute('SELECT * FROM Orbit_Details')
            orbit_details = cursor.fetchall()

            cursor.execute('SELECT * FROM Launch_Details')
            launch_details = cursor.fetchall()

            cursor.execute('SELECT * FROM Observer')
            observers = cursor.fetchall()

            cursor.execute('SELECT * FROM Obs_Coordinates')
            obs_coordinates = cursor.fetchall()

        satellites_with_details = []
        for satellite in satellites:
            satellite_observers = [observer for observer in observers if observer['Satellite_id'] == satellite['Satellite_id']]
            satellite_orbit = next((orbit for orbit in orbit_details if orbit['Satellite_id'] == satellite['Satellite_id']), None)
            satellite_launch_details = next((launch for launch in launch_details if launch['Launch_id'] == satellite['Launch_id']), None)

            satellite_coordinates = []
            for observer in satellite_observers:
                observer_id = observer['Observer_id']
                coordinates = next((coord for coord in obs_coordinates if coord['Observer_id'] == observer_id), None)
                if coordinates:
                    satellite_coordinates.append(coordinates)
        

            satellite['observers'] = satellite_observers
            satellite['orbit'] = satellite_orbit
            satellite['launch_details'] = satellite_launch_details
            satellite['coordinates'] = satellite_coordinates
            satellites_with_details.append(satellite)

        return render_template('update-info.html', launch_details=launch_details, satellites=satellites_with_details, obs_coordinates=obs_coordinates)
    
    except Exception as e:
        return f"An error occurred: {e}"
    
@routes_bp.route('/add-launch-details/', methods=['POST'])
def add_launch_details():
    if request.method == 'POST':
        launch_id = request.form['Launch_id']
        operator_name = request.form['Operator_Name']
        launch_site = request.form['Launch_Site']
        launch_vehicle = request.form['Launch_Vehicle']
        launch_date = request.form['Launch_Date']
        country = request.form['Country']

        try:
            with current_app.config['DB_CONNECTION'].cursor() as cursor:
                cursor.execute("INSERT INTO Launch_Details (Launch_id, Operator_Name, Launch_Site, Launch_Vehicle, Launch_Date, Country) VALUES (%s, %s, %s, %s, %s, %s)",
                               (launch_id, operator_name, launch_site, launch_vehicle, launch_date, country))
                current_app.config['DB_CONNECTION'].commit()
                return render_template('update-info.html', message='Launch details added successfully')
        except mysql.connector.Error as err:
            current_app.logger.error(f"An error occurred: {err}")
            return render_template('update-info.html', error='Failed to add launch details')


@routes_bp.route('/add-satellite/', methods=['POST'])
def add_satellite():
    if request.method == 'POST':
        name = request.form['Name']
        launch_id = request.form['Launch_id']
        launch_date = request.form['Launch_Date']
        country_of_origin = request.form['Country_of_Origin']
        payload = request.form['Payload']
        type = request.form['Type']
        status = request.form['Status']

        try:
            with current_app.config['DB_CONNECTION'].cursor() as cursor:
                cursor.execute("INSERT INTO Satellite ( Name, Launch_id, Launch_Date, Country_of_Origin, Payload, Type, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                               (name, launch_id, launch_date, country_of_origin, payload, type, status))
                current_app.config['DB_CONNECTION'].commit()
                return render_template('update-info.html', message='Satellite details added successfully')
        except mysql.connector.Error as err:
            current_app.logger.error(f"An error occurred: {err}")
            return render_template('update-info.html', error='Failed to add satellite details')


@routes_bp.route('/add-orbit-details/', methods=['POST'])
def add_orbit_details():
    if request.method == 'POST':
        satellite_id = request.form['Satellite_id']
        semi_major_axis = request.form['Semi_Major_Axis']
        orbital_period = request.form['Orbital_Period']
        apogee = request.form['Apogee']
        inclination = request.form['Inclination']
        prigee = request.form['Prigee']
        eccentricity = request.form['Eccentricity']

        try:
            with current_app.config['DB_CONNECTION'].cursor() as cursor:
                cursor.execute("INSERT INTO Orbit_Details (Satellite_id, Semi_Major_Axis, Orbital_Period, Apogee, Inclination, Prigee, Eccentricity) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                               (satellite_id, semi_major_axis, orbital_period, apogee, inclination, prigee, eccentricity))
                current_app.config['DB_CONNECTION'].commit()
                return render_template('update-info.html', message='Orbit details added successfully')
        except mysql.connector.Error as err:
            current_app.logger.error(f"An error occurred: {err}")
            return render_template('update-info.html', error='Failed to add orbit details')

@routes_bp.route('/add-observer/', methods=['POST'])
def add_observer():
    if request.method == 'POST':
        observer_id = request.form['Observer_id']
        satellite_id = request.form['Satellite_id']
        observer_name = request.form['Observer_Name']
        observer_location = request.form['Observer_Location']
        observation_date = request.form['Observation_Date']
        try:
            with current_app.config['DB_CONNECTION'].cursor() as cursor:
                cursor.execute("INSERT INTO Observer (Observer_id, Satellite_id, Observer_Name, Observer_Location, Observation_Date) VALUES (%s, %s, %s, %s, %s)",
                               (observer_id, satellite_id, observer_name, observer_location, observation_date))
                current_app.config['DB_CONNECTION'].commit()
                return render_template('update-info.html', message='Observer details added successfully')
        except mysql.connector.Error as err:
            current_app.logger.error(f"An error occurred: {err}")
            return render_template('update-info.html', error='Failed to add observer details')

@routes_bp.route('/add-observer-coordinates/', methods=['POST'])
def add_observer_coordinates():
    if request.method == 'POST':
        observer_id = request.form['Observer_id']
        country = request.form['Country']
        latitude = request.form['Latitude']
        longitude = request.form['Longitude']
        try:
            with current_app.config['DB_CONNECTION'].cursor() as cursor:
                cursor.execute("INSERT INTO Obs_Coordinates (Observer_id, Country, Latitude, Longitude) VALUES (%s, %s, %s, %s)",
                               (observer_id, country, latitude, longitude))
                current_app.config['DB_CONNECTION'].commit()
                return render_template('update-info.html', message='Observer coordinates added successfully')
        except mysql.connector.Error as err:
            current_app.logger.error(f"An error occurred: {err}")
            return render_template('update-info.html', error='Failed to add observer coordinates')


@routes_bp.route('/update_satellite/', methods=['GET', 'POST'])
def update_satellite():
    try:
        with current_app.config['DB_CONNECTION'].cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM Satellite 
                LEFT JOIN Orbit_Details ON Satellite.Satellite_id = Orbit_Details.Satellite_id
                LEFT JOIN Launch_Details ON Satellite.Launch_id = Launch_Details.Launch_id
                LEFT JOIN Observer ON Satellite.Satellite_id = Observer.Satellite_id
                LEFT JOIN Obs_Coordinates ON Observer.Observer_id = Obs_Coordinates.Observer_id
            """)
            satellite_data = cursor.fetchall()
            print(satellite_data)

        if request.method == 'POST':
            satellite_name = request.form['satellite_name']
            new_name = request.form['name']
            new_launch_date = request.form['launch_date']
            new_country_of_origin = request.form['country_of_origin']
            new_payload = request.form['payload']
            new_type = request.form['type']
            new_status = request.form['status']
            new_nord_id = request.form['nord_id']
            new_operator_name = request.form['operator_name']
            new_launch_site = request.form['launch_site']
            new_launch_vehicle = request.form['launch_vehicle']
            new_launch_date = request.form['new_launch_date']
            new_launch_country = request.form['new_launch_country']
            new_semi_major_axis = request.form['new_semi_major_axis']
            new_orbital_period = request.form['new_orbital_period']
            new_apogee = request.form['new_apogee']
            new_inclination = request.form['new_inclination']
            new_prigee = request.form['new_prigee']
            new_eccentricity = request.form['new_eccentricity']
            new_observer_name = request.form['observer_name']
            new_observer_location = request.form['observer_location']
            new_observation_date = request.form['observation_date']
            new_observer_country = request.form['observer_country']
            new_observer_latitude = request.form['observer_latitude']
            new_observer_longitude = request.form['observer_longitude']

            try:
                with current_app.config['DB_CONNECTION'].cursor() as cursor:
                    cursor.execute("""
                        UPDATE Satellite
                        JOIN Launch_Details ON Satellite.Launch_id = Launch_Details.Launch_id
                        JOIN Orbit_Details ON Satellite.Satellite_id = Orbit_Details.Satellite_id
                        JOIN Observer ON Satellite.Satellite_id = Observer.Satellite_id
                        JOIN Obs_Coordinates ON Observer.Observer_id = Obs_Coordinates.Observer_id
                        SET
                            Satellite.Name = %s,
                            Satellite.Launch_Date = %s,
                            Satellite.Country_of_Origin = %s,
                            Satellite.Payload = %s,
                            Satellite.Type = %s,
                            Satellite.Status = %s,
                            Satellite.nord_id = %s,
                            Launch_Details.Operator_Name = %s,
                            Launch_Details.Launch_Site = %s,
                            Launch_Details.Launch_Vehicle = %s,
                            Launch_Details.Launch_Date = %s,
                            Launch_Details.Country = %s,
                            Orbit_Details.Semi_Major_Axis = %s,
                            Orbit_Details.Orbital_Period = %s,
                            Orbit_Details.Apogee = %s,
                            Orbit_Details.Inclination = %s,
                            Orbit_Details.Prigee = %s,
                            Orbit_Details.Eccentricity = %s,
                            Observer.Observer_Name = %s,
                            Observer.Observer_Location = %s,
                            Observer.Observation_Date = %s,
                            Obs_Coordinates.Country = %s,
                            Obs_Coordinates.Latitude = %s,
                            Obs_Coordinates.Longitude = %s
                        WHERE
                            Satellite.Name = %s
                    """, (new_name, new_launch_date, new_country_of_origin, new_payload, new_type, new_status, new_nord_id,
                          new_operator_name, new_launch_site, new_launch_vehicle, new_launch_date, new_launch_country,
                          new_semi_major_axis, new_orbital_period, new_apogee, new_inclination, new_prigee,
                          new_eccentricity, new_observer_name, new_observer_location, new_observation_date,
                          new_observer_country, new_observer_latitude, new_observer_longitude, satellite_name))
                    current_app.config['DB_CONNECTION'].commit()
                    return render_template('update-info.html', satellites=satellite_data, message='Satellite and related data updated successfully')
            except mysql.connector.Error as err:
                current_app.logger.error(f"An error occurred: {err}")
                return render_template('update-info.html', satellites=satellite_data, error='Failed to update satellite data')

    except mysql.connector.Error as err:
        current_app.logger.error(f"An error occurred: {err}")
        return render_template('update-info.html', error='Failed to fetch satellite data')

@routes_bp.route('/delete-satellite/<string:satellite_name>', methods=['POST'])
def delete_satellite(satellite_name):
    try:
        with current_app.config['DB_CONNECTION'].cursor() as cursor:
            cursor.execute("DELETE FROM satellite WHERE Name = %s", (satellite_name,))
            current_app.config['DB_CONNECTION'].commit()
            return redirect(url_for('routes.home')) 
    except mysql.connector.Error as err:
        return render_template('index.html', error=str(err)), 500

@routes_bp.route('/delete-satellite-data/', methods=['POST'])
def delete_satellite_data():
    try:
        satellite_name = request.form['satellite_name']
        with current_app.config['DB_CONNECTION'].cursor() as cursor:
            cursor.callproc("delete_satellite_data_procedure", [satellite_name])  
            current_app.config['DB_CONNECTION'].commit()
            return redirect(url_for('routes.home'))  
    except mysql.connector.Error as err:
        return render_template('index.html', error=str(err)), 500