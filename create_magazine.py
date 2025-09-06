import json
import requests
import os
from pathlib import Path

# Get the guide data
response = requests.get('http://localhost:8000/api/enhanced-guide/7f118583-684b-496b-a43f-d9e2e83fc9eb')
guide_data = response.json()

# Extract dynamic data
destination = guide_data.get('guide', {}).get('destination', 'Unknown Destination')
start_date = guide_data.get('guide', {}).get('start_date', 'Unknown Date')
end_date = guide_data.get('guide', {}).get('end_date', 'Unknown Date')

# Create HTML magazine
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Condé Nast Traveler - New York City</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Georgia', serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }
        
        .magazine-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .cover {
            text-align: center;
            padding: 60px 0;
            background: linear-gradient(135deg, #1a1a1a 0%, #2E86AB 100%);
            color: white;
            margin-bottom: 40px;
            border-radius: 8px;
        }
        
        .cover h1 {
            font-size: 3.5rem;
            font-weight: 300;
            letter-spacing: 2px;
            margin-bottom: 20px;
        }
        
        .cover h2 {
            font-size: 2rem;
            font-weight: 300;
            margin-bottom: 10px;
        }
        
        .cover .date {
            font-size: 1.2rem;
            opacity: 0.8;
        }
        
        .section {
            margin: 60px 0;
            padding: 40px;
            background: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 2.5rem;
            color: #A23B72;
            margin-bottom: 30px;
            text-align: center;
            font-weight: 300;
            letter-spacing: 1px;
        }
        
        .weather-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .weather-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #2E86AB;
        }
        
        .weather-day {
            font-size: 1.2rem;
            font-weight: bold;
            color: #2E86AB;
            margin-bottom: 10px;
        }
        
        .weather-temp {
            font-size: 2rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .weather-condition {
            font-size: 1.5rem;
            margin: 10px 0;
        }
        
        .weather-note {
            font-size: 0.9rem;
            color: #666;
            font-style: italic;
        }
        
        .hotel-feature {
            background: white;
            padding: 40px;
            border-radius: 8px;
            margin: 30px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .hotel-name {
            font-size: 2rem;
            color: #2E86AB;
            margin-bottom: 20px;
        }
        
        .editorial-content {
            font-size: 1.1rem;
            line-height: 1.8;
            margin: 20px 0;
            text-align: justify;
        }
        
        .restaurant-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }
        
        .restaurant-card {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 4px solid #A23B72;
        }
        
        .restaurant-header {
            font-size: 1.5rem;
            color: #2E86AB;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .restaurant-rating {
            color: #A23B72;
            font-weight: bold;
        }
        
        .restaurant-photo {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .restaurant-details {
            margin: 15px 0;
        }
        
        .restaurant-details strong {
            color: #2E86AB;
        }
        
        .attraction-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }
        
        .attraction-card {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 4px solid #2E86AB;
        }
        
        .attraction-header {
            font-size: 1.5rem;
            color: #A23B72;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .attraction-photo {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .insider-tip {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            margin: 20px 0;
        }
        
        .insider-tip strong {
            color: #2E86AB;
        }
        
        .booking-info {
            background: #f0f8f0;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #28a745;
        }
        
        .booking-info strong {
            color: #28a745;
        }
        
        .practical-info {
            background: white;
            padding: 40px;
            border-radius: 8px;
            margin: 30px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .practical-section {
            margin: 25px 0;
        }
        
        .practical-section h3 {
            color: #A23B72;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        .event-category {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 4px solid #2E86AB;
        }
        
        .event-category-title {
            font-size: 1.4rem;
            color: #A23B72;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .event-venues {
            margin: 15px 0;
        }
        
        .venue-tag {
            display: inline-block;
            background: #e8f4f8;
            color: #2E86AB;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 3px 5px 3px 0;
            font-weight: 500;
        }
        
        .sports-info {
            margin: 15px 0;
        }
        
        .sport-match {
            background: #f0f8f0;
            padding: 10px;
            border-radius: 6px;
            margin: 8px 0;
            border-left: 3px solid #28a745;
        }
        
        .event-themes {
            background: #fff3cd;
            padding: 10px;
            border-radius: 6px;
            margin: 15px 0;
            border-left: 3px solid #ffc107;
        }
        
        .event-details {
            margin: 15px 0;
        }
        
        .event-date-time,
        .event-venue,
        .event-address,
        .event-price {
            margin: 8px 0;
            font-size: 0.95rem;
        }
        
        .event-date-time strong,
        .event-venue strong,
        .event-address strong,
        .event-price strong {
            color: #2E86AB;
        }
        
        .event-photo {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        .event-description {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .event-booking {
            margin: 10px 0;
        }
        
        .booking-link {
            display: inline-block;
            background: #A23B72;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            transition: background 0.3s;
        }
        
        .booking-link:hover {
            background: #8a2f5f;
        }
        
        .event-source {
            font-size: 0.8rem;
            color: #666;
            font-style: italic;
            margin-top: 10px;
        }
        
        .itinerary-container {
            margin: 30px 0;
        }
        
        .itinerary-day {
            background: white;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .day-header {
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .day-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0;
        }
        
        .day-date {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .day-activities {
            padding: 25px;
        }
        
        .activity-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 4px solid #2E86AB;
            font-size: 1rem;
            line-height: 1.6;
        }
        
        .day-details {
            background: #f8f9fa;
            padding: 20px 25px;
            border-top: 1px solid #e9ecef;
        }
        
        .transport-info,
        .cost-info {
            margin: 10px 0;
            font-size: 0.95rem;
        }
        
        .transport-info strong,
        .cost-info strong {
            color: #2E86AB;
        }
        
        @media (max-width: 768px) {
            .magazine-container {
                padding: 10px;
            }
            
            .cover h1 {
                font-size: 2.5rem;
            }
            
            .section {
                padding: 20px;
            }
            
            .restaurant-grid,
            .attraction-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="magazine-container">
        <!-- Cover Page -->
        <div class="cover">
            <h1>CONDÉ NAST TRAVELER</h1>
            <h2>{destination}</h2>
            <p class="date">{start_date} to {end_date}</p>
        </div>
        
        <!-- Weather Section -->
        <div class="section">
            <h2 class="section-title">WEATHER & WHEN TO GO</h2>
            <div class="editorial-content">
                {destination} offers a unique blend of cultural richness and local charm. 
                The city's vibrant atmosphere and diverse offerings make it an ideal destination 
                for travelers seeking authentic experiences. This guide will help you discover 
                the best of what {destination} has to offer during your visit.
            </div>
            
            <div class="weather-grid">
                <div class="weather-card">
                    <div class="weather-day">Nov 10</div>
                    <div class="weather-temp">13°C / 6°C</div>
                    <div class="weather-condition">☁️ Cloudy</div>
                    <div class="weather-note">Perfect for museum hopping and indoor dining</div>
                </div>
                <div class="weather-card">
                    <div class="weather-day">Nov 11</div>
                    <div class="weather-temp">15°C / 8°C</div>
                    <div class="weather-condition">🌧️ Light Rain</div>
                    <div class="weather-note">Ideal for cozy café culture and shopping</div>
                </div>
                <div class="weather-card">
                    <div class="weather-day">Nov 12</div>
                    <div class="weather-temp">12°C / 5°C</div>
                    <div class="weather-condition">☁️ Partly Cloudy</div>
                    <div class="weather-note">Great for walking tours and outdoor markets</div>
                </div>
                <div class="weather-card">
                    <div class="weather-day">Nov 13</div>
                    <div class="weather-temp">14°C / 7°C</div>
                    <div class="weather-condition">☀️ Sunny</div>
                    <div class="weather-note">Perfect for Central Park and rooftop bars</div>
                </div>
            </div>
        </div>
'''

# Add hotel section
if guide_data.get('guide', {}).get('hotel_info'):
    hotel = guide_data['guide']['hotel_info']
    hotel_name = hotel.get('name', 'Unknown Hotel')
    hotel_address = hotel.get('address', 'No address')
    hotel_phone = hotel.get('phone', 'No phone')
    check_in = hotel.get('check_in_date', 'Unknown')
    check_out = hotel.get('check_out_date', 'Unknown')
    
    html_content += f'''
        <!-- Hotel Section -->
        <div class="section">
            <h2 class="section-title">WHERE TO STAY</h2>
            <div class="hotel-feature">
                <h3 class="hotel-name">{hotel_name}</h3>
                <div class="editorial-content">
                    There's something undeniably magical about waking up in the heart of Manhattan, and {hotel_name} delivers this experience with unparalleled sophistication. 
                    This isn't just a place to rest your head—it's a destination in itself, where every detail has been carefully curated to create an atmosphere of refined luxury.
                    <br><br>
                    The location is nothing short of spectacular. Situated at {hotel_address}, you're perfectly positioned to explore 
                    the city's most iconic neighborhoods. Whether you're strolling through Central Park in the morning or catching a Broadway show in the evening, 
                    everything feels within reach.
                    <br><br>
                    What sets this property apart is its commitment to creating memorable experiences. The staff anticipates your needs before you even realize them, 
                    and the attention to detail extends from the plush linens to the carefully selected artwork that adorns the walls. It's the kind of place where 
                    you'll find yourself planning your next visit before you've even checked out.
                </div>
                
                <div class="booking-info">
                    <strong>Essential Details:</strong><br>
                    Address: {hotel_address}<br>
                    Phone: {hotel_phone}<br>
                    Check-in: {check_in} • Check-out: {check_out}
                </div>
                
                <div class="insider-tip">
                    <strong>Why We Love It:</strong> This is where Manhattan's energy meets refined comfort. Perfect for travelers who want to be in the center of it all 
                    while enjoying the kind of service that makes you feel like a VIP.
                </div>
            </div>
        </div>
    '''

# Add restaurants section
if guide_data.get('guide', {}).get('restaurants'):
    html_content += '''
        <!-- Restaurants Section -->
        <div class="section">
            <h2 class="section-title">WHERE TO EAT</h2>
            <div class="restaurant-grid">
    '''
    
    for restaurant in guide_data['guide']['restaurants'][:6]:  # Top 6 restaurants
        name = restaurant.get('name', 'Unknown')
        rating = restaurant.get('rating', 'N/A')
        cuisine = restaurant.get('cuisine', 'Unknown cuisine')
        description = restaurant.get('description', 'No description')
        address = restaurant.get('address', 'No address')
        phone = restaurant.get('phone', 'No phone')
        website = restaurant.get('website', '')
        booking_url = restaurant.get('primary_booking_url', '')
        main_photo = restaurant.get('main_photo', '')
        price_range = restaurant.get('price_range', '')
        best_dishes = restaurant.get('best_dishes', [])
        visit_tips = restaurant.get('visit_tips', '')
        
        html_content += f'''
                <div class="restaurant-card">
                    <h3 class="restaurant-header">{name} <span class="restaurant-rating">• {rating}★</span></h3>
                    <p><strong>Cuisine:</strong> {cuisine}</p>
        '''
        
        if main_photo:
            html_content += f'<img src="{main_photo}" alt="{name}" class="restaurant-photo" onerror="this.style.display=\'none\'">'
        
        html_content += f'''
                    <div class="editorial-content">
                        {description}
                        <br><br>
                        This is the kind of place that makes New York dining legendary. The atmosphere crackles with the energy of a city that never sleeps, 
                        while the food tells a story of culinary excellence that spans generations. Every dish is a celebration of flavor, technique, and the 
                        vibrant spirit of Manhattan.
                    </div>
                    
                    <div class="restaurant-details">
                        <strong>Address:</strong> {address}<br>
                        <strong>Phone:</strong> {phone}<br>
        '''
        
        if price_range:
            html_content += f'<strong>Price Range:</strong> {price_range}<br>'
        if best_dishes and len(best_dishes) > 0:
            dishes_text = ", ".join(best_dishes[:3])  # Show top 3 dishes
            html_content += f'<strong>Must-Try:</strong> {dishes_text}<br>'
        
        if website:
            html_content += f'<strong>Website:</strong> <a href="{website}" target="_blank">{website}</a><br>'
        if booking_url:
            html_content += f'<strong>Reservations:</strong> <a href="{booking_url}" target="_blank">Book Now</a><br>'
        
        html_content += '''
                    </div>
                    
                    <div class="insider-tip">
        '''
        
        if visit_tips:
            html_content += f'<strong>Insider Tip:</strong> {visit_tips}'
        else:
            html_content += '<strong>Insider Tip:</strong> Book well in advance, especially for weekend dining. The bar area offers a more casual experience with the same exceptional quality.'
        
        html_content += '''
                    </div>
                </div>
        '''
    
    html_content += '''
            </div>
        </div>
    '''

# Add attractions section
if guide_data.get('guide', {}).get('attractions'):
    html_content += '''
        <!-- Attractions Section -->
        <div class="section">
            <h2 class="section-title">WHAT TO SEE</h2>
            <div class="attraction-grid">
    '''
    
    for attraction in guide_data['guide']['attractions'][:6]:  # Top 6 attractions
        name = attraction.get('name', 'Unknown')
        rating = attraction.get('rating', 'N/A')
        description = attraction.get('description', 'No description')
        address = attraction.get('address', 'No address')
        hours = attraction.get('hours', [])
        open_now = attraction.get('open_now', None)
        visit_duration = attraction.get('visit_duration', '')
        best_time = attraction.get('best_time_to_visit', '')
        website = attraction.get('website', '')
        booking_url = attraction.get('primary_booking_url', '')
        main_photo = attraction.get('main_photo', '')
        
        # Format hours information
        hours_text = "Hours vary by season"
        if hours and len(hours) > 0:
            hours_text = "<br>".join(hours)
        elif open_now is not None:
            hours_text = "Open 24/7" if open_now else "Check website for current hours"
        
        html_content += f'''
                <div class="attraction-card">
                    <h3 class="attraction-header">{name} <span class="restaurant-rating">• {rating}★</span></h3>
        '''
        
        if main_photo:
            html_content += f'<img src="{main_photo}" alt="{name}" class="attraction-photo" onerror="this.style.display=\'none\'">'
        
        html_content += f'''
                    <div class="editorial-content">
                        {description}
                        <br><br>
                        This is one of those places that defines what it means to experience New York. The moment you arrive, you understand why millions of 
                        visitors make the pilgrimage here each year. It's not just about seeing something famous—it's about connecting with the soul of the city 
                        and understanding what makes New York truly extraordinary.
                    </div>
                    
                    <div class="restaurant-details">
                        <strong>Address:</strong> {address}<br>
                        <strong>Hours:</strong> {hours_text}<br>
        '''
        
        if visit_duration:
            html_content += f'<strong>Visit Duration:</strong> {visit_duration}<br>'
        if best_time:
            html_content += f'<strong>Best Time to Visit:</strong> {best_time}<br>'
        
        if website:
            html_content += f'<strong>Website:</strong> <a href="{website}" target="_blank">{website}</a><br>'
        if booking_url:
            html_content += f'<strong>Tickets:</strong> <a href="{booking_url}" target="_blank">Book Now</a><br>'
        
        html_content += '''
                    </div>
                    
                    <div class="insider-tip">
                        <strong>Insider Tip:</strong> Visit during off-peak hours for a more intimate experience. The early morning or late afternoon often offer the best lighting and fewer crowds.
                    </div>
                </div>
        '''
    
    html_content += '''
            </div>
        </div>
    '''

# Add events and what's on section
if guide_data.get('guide', {}).get('events'):
    events_data = guide_data['guide']['events']
    html_content += '''
        <!-- Events & What's On Section -->
        <div class="section">
            <h2 class="section-title">WHAT'S ON THIS WEEK</h2>
            <div class="editorial-content">
                {destination} is alive with cultural energy and exciting events. From world-class performances 
                to cutting-edge exhibitions, the city offers an unparalleled array of entertainment and cultural experiences. 
                This is the perfect time to immerse yourself in the vibrant local scene and discover what makes {destination} special.
            </div>
            
            <div class="events-grid">
    '''
    
    # Check if we have real events from APIs
    if events_data.get('real_events'):
        # Display real events with specific dates and venues
        for event in events_data['real_events'][:8]:  # Show top 8 real events
            name = event.get('name', 'Unknown Event')
            event_type = event.get('type', 'Event')
            date = event.get('date', '')
            time = event.get('time', '')
            venue = event.get('venue', '')
            address = event.get('address', '')
            price_range = event.get('price_range', 'Price varies')
            description = event.get('description', '')
            booking_url = event.get('booking_url', '')
            image_url = event.get('image_url', '')
            source = event.get('source', '')
            
            html_content += f'''
                <div class="event-category">
                    <h3 class="event-category-title">{name}</h3>
                    <div class="event-details">
                        <div class="event-date-time">
                            <strong>Date:</strong> {date} {time}
                        </div>
                        <div class="event-venue">
                            <strong>Venue:</strong> {venue}
                        </div>
                        <div class="event-address">
                            <strong>Location:</strong> {address}
                        </div>
                        <div class="event-price">
                            <strong>Price:</strong> {price_range}
                        </div>
            '''
            
            if image_url:
                html_content += f'<img src="{image_url}" alt="{name}" class="event-photo" onerror="this.style.display=\'none\'">'
            
            if description:
                html_content += f'<div class="event-description">{description}</div>'
            
            if booking_url:
                html_content += f'<div class="event-booking"><a href="{booking_url}" target="_blank" class="booking-link">Get Tickets</a></div>'
            
            html_content += f'''
                        <div class="event-source">Source: {source}</div>
                    </div>
                </div>
            '''
    
    # Fallback to typical events if no real events
    elif events_data.get('typical_events'):
        for event_type in events_data['typical_events']:
            event_name = event_type.get('type', 'Unknown Event')
            html_content += f'''
                <div class="event-category">
                    <h3 class="event-category-title">{event_name}</h3>
            '''
            
            if event_type.get('venues'):
                html_content += '<div class="event-venues">'
                for venue in event_type['venues']:
                    html_content += f'<span class="venue-tag">{venue}</span>'
                html_content += '</div>'
            
            if event_type.get('sports'):
                html_content += '<div class="sports-info">'
                for sport in event_type['sports']:
                    league = sport.get('league', '')
                    teams = sport.get('teams', [])
                    if league and teams:
                        teams_text = " vs ".join(teams)
                        html_content += f'<div class="sport-match"><strong>{league}:</strong> {teams_text}</div>'
                html_content += '</div>'
            
            if event_type.get('themes'):
                themes = event_type['themes']
                themes_text = ", ".join(themes)
                html_content += f'<div class="event-themes"><strong>Seasonal Focus:</strong> {themes_text}</div>'
            
            html_content += '''
                </div>
            '''
    
    html_content += '''
            </div>
        </div>
    '''

# Add daily itinerary section
if guide_data.get('guide', {}).get('daily_itinerary'):
    html_content += '''
        <!-- Daily Itinerary Section -->
        <div class="section">
            <h2 class="section-title">YOUR PERSONALIZED ITINERARY</h2>
            <div class="editorial-content">
                We've crafted a carefully curated four-day itinerary that balances iconic landmarks with hidden gems, 
                ensuring you experience the very best of New York City. Each day is designed to maximize your time 
                while allowing for spontaneous discoveries and local experiences.
            </div>
            
            <div class="itinerary-container">
    '''
    
    for day in guide_data['guide']['daily_itinerary']:
        day_num = day.get('day', 0)
        date = day.get('date', '')
        activities = day.get('activities', [])
        transport = day.get('transport_notes', '')
        cost = day.get('estimated_cost', '')
        
        # Format date nicely
        if date:
            from datetime import datetime
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d')
            except:
                formatted_date = date
        else:
            formatted_date = f"Day {day_num}"
        
        html_content += f'''
                <div class="itinerary-day">
                    <div class="day-header">
                        <h3 class="day-title">Day {day_num}</h3>
                        <span class="day-date">{formatted_date}</span>
                    </div>
                    
                    <div class="day-activities">
        '''
        
        for activity in activities:
            html_content += f'<div class="activity-item">{activity}</div>'
        
        html_content += f'''
                    </div>
                    
                    <div class="day-details">
                        <div class="transport-info">
                            <strong>Getting Around:</strong> {transport}
                        </div>
                        <div class="cost-info">
                            <strong>Estimated Cost:</strong> {cost}
                        </div>
                    </div>
                </div>
        '''
    
    html_content += '''
            </div>
        </div>
    '''

# Add practical information
html_content += '''
        <!-- Practical Information -->
        <div class="section">
            <h2 class="section-title">ESSENTIAL INFORMATION</h2>
            <div class="practical-info">
                <div class="practical-section">
                    <h3>Getting Around</h3>
                    <div class="editorial-content">
                        New York's subway system is the most efficient way to navigate the city. Purchase a MetroCard or use contactless payment. 
                        Taxis and ride-sharing services are readily available. Walking is often the best way to experience the city's energy and discover hidden gems.
                    </div>
                </div>
                
                <div class="practical-section">
                    <h3>Currency & Payments</h3>
                    <div class="editorial-content">
                        US Dollar (USD). Credit cards are widely accepted, but carry some cash for small purchases, street vendors, and tips. 
                        Most establishments accept contactless payments.
                    </div>
                </div>
                
                <div class="practical-section">
                    <h3>Emergency Information</h3>
                    <div class="editorial-content">
                        911 for police, fire, and medical emergencies. 311 for non-emergency city services. Keep your hotel's address and phone number handy.
                    </div>
                </div>
                
                <div class="practical-section">
                    <h3>Local Customs & Tips</h3>
                    <div class="editorial-content">
                        New Yorkers walk fast and expect the same from visitors. Stand to the right on escalators, and don't block subway doors. 
                        Tipping 18-20% is standard for restaurants and services. Be prepared for the city's energy and embrace the pace.
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Format HTML content with dynamic data
html_content = html_content.format(
    destination=destination,
    start_date=start_date,
    end_date=end_date
)

# Write HTML file
with open('conde_nast_magazine.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Condé Nast magazine HTML created successfully: conde_nast_magazine.html')
