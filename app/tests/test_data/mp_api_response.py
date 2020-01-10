test_user_data = {
    'id': 105324100,
    'name': 'Test User',
    'memberSince': '2011-10-10',
    'lastVisit_mtb': '0000-00-00',
    'lastVisit_hike': '0000-00-00',
    'lastVisit_ski': '0000-00-00',
    'lastVisit_trailrun': '0000-00-00',
    'lastVisit_climb': '2020-01-09',
    'favoriteClimbs': '',
    'otherInterests': '',
    'postalCode': '',
    'location': '',
    'url': 'https://www.mountainproject.com/user/107324100/test-user',
    'personalText': '',
    'styles': {'Trad': {'lead': '', 'follow': ''},
               'Sport': {'lead': '', 'follow': ''},
               'Aid': {'lead': '', 'follow': ''},
               'Ice': {'lead': '', 'follow': ''},
               'Mixed': {'lead': '', 'follow': ''},
               'Boulders': {'lead': '', 'follow': ''}},
    'avatar': 'https://cdn.apstatic.com/img/user/missing2.svg',
    'pts_mtb': 0,
    'pts_hike': 0,
    'pts_ski': 0,
    'pts_trailrun': 0,
    'pts_climb': 0,
    'admin': '',
    'success': 1
}

test_ticks_response = b'Date,Route,Rating,Notes,URL,Pitches,Location,"Avg Stars","Your Stars",Style,"Lead Style","Route Type","Your Rating",Length,"Rating Code"\n2018-06-01,Sprayathon,5.13c,,https://www.mountainproject.com/route/105753589/sprayathon,1,"Colorado > Rifle > Rifle Mountain Park > The Arsenal",3.9,-1,Lead,Redpoint,Sport,,,9200\n'
test_expected_data = [['2018-06-01', 'Sprayathon', '1', 'Lead', 'Redpoint', 'Sport', '', '9200']]