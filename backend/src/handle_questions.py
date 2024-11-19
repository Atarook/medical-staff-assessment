"""Provide questions for the frontend to display and handle the submission of answers."""
import json
from datetime import date, timedelta

from django.http import JsonResponse

from ..models import (CareServiceOption, DailyClassification,
                      IsCareServiceUsed, Patient)
from .handle_calculations import calculate_care_minutes


def add_selected_attribute(care_service_options: list, patient_id: int) -> list:
    """Add the attribute if the care service was previously selected or not.

    Args:
        care_service_options (list): The care service options to which to add the 'selected' attribute.
        patient_id (int): The ID of the patient to look for previous classifications.

    Returns:
        list: The care service options with the attribute if they were previously selected or not.
    """
    # If patient does not exist, return the questions without the attribute
    if not Patient.objects.filter(id=patient_id).exists():
        return [{**option, 'selected': False} for option in care_service_options]

    # Get the ID of the previous classification
    previous_date = date.today() - timedelta(days=1)
    previous_classification = list(DailyClassification.objects.filter(
        patient_id=patient_id,
        classification_date=previous_date,
    ).values('id'))

    # If no previous classification exists, return the questions without the attribute
    if len(previous_classification) == 0:
        return [{**option, 'selected': False} for option in care_service_options]

    # Get all previous selected care services
    previous_selected_services = list(IsCareServiceUsed.objects.filter(
        classification_id=previous_classification[0]['id'],
    ).values('care_service_id'))

    # Add the attribute if the care service was previously selected or not
    for option in care_service_options:
        option['selected'] = any(
            previous_service['care_service_id'] == option['id']
            for previous_service in previous_selected_services
        )

    return care_service_options


def get_questions(patient_id: int) -> list:
    """Get the questions from the database.

    Args:
        patient_id (int): The ID of the patient.

    Returns:
        list: The questions from the database and the attribute if they were previously selected or not.
    """
    # Get the questions with the corresponding information
    care_service_options = list(
        CareServiceOption.objects.select_related('field_id', 'category_id').values(
            'id',
            'field_id__name',
            'field_id__short',
            'category_id__name',
            'name',
            'severity',
            'description',
        )
    )

    return add_selected_attribute(care_service_options, patient_id)


def has_missing_data(body: dict) -> bool:
    """Check if the body of the request contains all necessary information.

    Args:
        body (dict): The body of the request.

    Returns:
        bool: True if the body is missing information, False otherwise.
    """
    return ('is_in_isolation' not in body
            or 'data_accepted' not in body
            or 'station_id' not in body
            or 'room_name' not in body
            or 'bed_number' not in body
            or 'barthel_index' not in body
            or 'expanded_barthel_index' not in body
            or 'mini_mental_status' not in body
            or 'selected_care_services' not in body)


def submit_selected_options(patient_id: int, body: dict) -> JsonResponse:
    """Save the questions to the database.

    Args:
        patient_id (int): The ID of the patient.
        body (dict): The body of the request containing the selected care services and more information.
    """
    # Check if the body contains all necessary information
    if has_missing_data(body):
        return JsonResponse({'message': 'Missing information in the request.'}, status=400)

    # Create the classification entry
    patient = Patient.objects.get(id=patient_id)
    minutes_to_take_care = calculate_care_minutes(body)
    classification = DailyClassification.objects.create(
        patient_id=patient,
        classification_date=date.today(),
        is_in_isolation=body['is_in_isolation'],
        data_accepted=body['data_accepted'],
        result_minutes=minutes_to_take_care,
        station_id=body['station_id'],
        room_name=body['room_name'],
        bed_number=body['bed_number'],
    )

    # Save the selected care services
    for care_service in body['selected_care_services']:
        care_service = CareServiceOption.objects.get(id=care_service['id'])
        IsCareServiceUsed.objects.create(
            classification_id=classification,
            care_service_option_id=care_service,
        )

    return JsonResponse({'message': 'Successfully saved the selected care services.'}, status=200)


def handle_questions(request, patient_id: int) -> JsonResponse:
    """Endpoint to handle the submission and pulling of questions.

    Args:
        request (Request): The request
        patient_id (int): The ID of the patient.

    Returns:
        JsonResponse: The response send back to the client depending on the type of request
    """
    if request.method == 'POST':
        # Handle the submission of questions
        body_data = json.loads(request.body)
        return submit_selected_options(patient_id, body_data)
    elif request.method == 'GET':
        # Handle the pulling of questions for a patient
        return JsonResponse(get_questions(patient_id), safe=False)
