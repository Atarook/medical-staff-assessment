from django.shortcuts import render
from backend.models import Station


def home(request):
    return render(request, 'frontend/home.html')


def analysis(request):
    return render(request, 'frontend/analysis.html')


def stations(request):
    # all_stations = Station.objects.all()  # Retrieve all stations from the database
    all_stations = [
        Station(id=i, name=f'Station {i}', is_intensive_care=False, is_child_care_unit=False,
                patients_per_caregiver_ratio=1.5 + i * 0.1)
        for i in range(1, 11)
    ]

    context = {
        'stations': all_stations
    }
    return render(request, 'frontend/stations.html', context)


def station_patient_list(request, id):
    # Hardcoded patients assigned to the station
    hardcoded_patients = [
        {
            "id": 1,
            "first_name": "Alice",
            "last_name": "Smith",
            "daily_today": True,
            "station_id": 1,
        },
        {
            "id": 2,
            "first_name": "Bob",
            "last_name": "Johnson",
            "daily_today": True,
            "station_id": 1,
        },
        {
            "id": 3,
            "first_name": "Charlie",
            "last_name": "Williams",
            "daily_today": False,
            "station_id": 1,
        },
        {
            "id": 4,
            "first_name": "Diana",
            "last_name": "Brown",
            "daily_today": True,
            "station_id": 1, 
        },
        {
            "id": 5,
            "first_name": "Edward",
            "last_name": "Davis",
            "daily_today": True, 
            "station_id": 1,
        },
        {
            "id": 6,
            "first_name": "Fiona",
            "last_name": "Clark",
            "daily_today": True,
            "station_id": 1,
        },
        {
            "id": 7,
            "first_name": "George",
            "last_name": "Harris",
            "daily_today": False,
            "station_id": 3,
        },
        {
            "id": 8,
            "first_name": "Hannah",
            "last_name": "Lewis",
            "daily_today": True,
            "station_id": 4,
        },
        {
            "id": 9,
            "first_name": "Ian",
            "last_name": "Walker",
            "daily_today": False,
            "station_id": 2,
        },
        {
            "id": 10,
            "first_name": "Julia",
            "last_name": "King",
            "daily_today": True,
            "station_id": 5,
        },
    ]

    context = {
        'id': id,  # Station ID
        'patients': hardcoded_patients,  # Pass the hardcoded patients to the template
    }
    return render(request, 'frontend/station_patient_list.html', context)


def classification(request, id, patient_id, date):
    context = {
        'id': id,
        'patient_id': patient_id,
        'date': date  # TODO parse and validate this
    }
    return render(request, 'frontend/classification.html', context)
