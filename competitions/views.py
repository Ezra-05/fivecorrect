from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Competition, Match, Prediction, CompetitionResult
from .forms import PredictionForm
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Sum, Min, F, Value
# New added
from django.contrib import messages

from django.db.models.functions import Coalesce
from collections import namedtuple


User = get_user_model()

@login_required
def competition_listold(request):
    competitions = Competition.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'competitions/competition_list.html', {'competitions': competitions})

@login_required
def competition_list(request):
    competitions = Competition.objects.order_by('-published_date')
    print(competitions)
    return render(request, 'competitions/competition_list.html', {'competitions': competitions})

@login_required
def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    matches = competition.match_set.all()
    predictions = Prediction.objects.filter(match__in=matches, user=request.user)
    return render(request, 'competitions/competition_detail.html', {'competition': competition, 'matches': matches, 'predictions': predictions})

@login_required
def make_predictionold(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.match = match
            prediction.save()
            return redirect('competition_detail', competition_id=match.competition.id)
    else:
        form = PredictionForm()

    return render(request, 'competitions/make_prediction.html', {'form': form, 'match': match})

@login_required
def make_predictionold2(request, match_id):
    match = Match.objects.get(id=match_id)
    competition = match.competition

    # Check if the user has already made a prediction for this match
    if Prediction.objects.filter(user=request.user, match=match).exists():
        messages.error(request, 'You have already made a prediction for this match.')
        return redirect('leaderboard')

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.match = match
            prediction.save()
            messages.success(request, 'Your prediction has been submitted.')
            return redirect('leaderboard')
    else:
        form = PredictionForm()

    return render(request, 'competitions/make_prediction.html', {'form': form, 'match': match})

@login_required
def make_predictionold3(request, match_id):
    match = Match.objects.get(id=match_id)
    competition = match.competition

    # Check if the user has already made a prediction for this match
    existing_prediction = Prediction.objects.filter(user=request.user, match=match).first()
    
    if existing_prediction:
        messages.error(request, 'You have already made a prediction for this match.')
        return redirect('leaderboard')

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            # Save the prediction only if it doesn't exist
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.match = match
            try:
                prediction.save()
                messages.success(request, 'Your prediction has been submitted.')
                return redirect('leaderboard')
            except IntegrityError:
                messages.error(request, 'You have already made a prediction for this match.')
                return redirect('leaderboard')
    else:
        form = PredictionForm()

    return render(request, 'competitions/make_prediction.html', {'form': form, 'match': match})

@login_required
def make_predictionold4(request, match_id):
    match = Match.objects.get(id=match_id)
    competition = match.competition

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction_data = form.save(commit=False)
            prediction_data.user = request.user
            prediction_data.match = match

            # Use get_or_create to prevent duplicate entries
            prediction, created = Prediction.objects.get_or_create(
                user=request.user,
                match=match,
                defaults={
                    'predicted_home_team_score': prediction_data.predicted_home_team_score,
                    'predicted_away_team_score': prediction_data.predicted_away_team_score,
                    'golden_goal': prediction_data.golden_goal,
                }
            )

            if created:
                messages.success(request, 'Your prediction has been submitted.')
            else:
                messages.error(request, 'You have already made a prediction for this match.')

            return redirect('leaderboard')

    else:
        form = PredictionForm()

    return render(request, 'competitions/make_prediction.html', {'form': form, 'match': match})

@login_required
def make_predictionold5(request, match_id):
    match = Match.objects.get(id=match_id)
    competition = match.competition

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction_data = form.save(commit=False)
            prediction_data.user = request.user
            prediction_data.match = match

            try:
                with transaction.atomic():
                    # prediction = Prediction.objects.create(
                    #     user=request.user,
                    #     match=match,
                    #     predicted_home_team_score=prediction_data.predicted_home_team_score,
                    #     predicted_away_team_score=prediction_data.predicted_away_team_score,
                    #     golden_goal=prediction_data.golden_goal,
                    # )
                    prediction, created = Prediction.objects.get_or_create(
                    user=request.user,
                    match=match,
                    defaults={
                    'predicted_home_team_score': prediction_data.predicted_home_team_score,
                    'predicted_away_team_score': prediction_data.predicted_away_team_score,
                    'golden_goal': prediction_data.golden_goal,
                }
            )

                    if created:
                        messages.success(request, 'Your prediction has been submitted.')
                    else:
                        messages.error(request, 'You have already made a prediction for this match.')

                    return redirect('leaderboard')

            except IntegrityError:
                messages.error(request, 'You have already made a prediction for this match.')
                return redirect('leaderboard')

    else:
        form = PredictionForm()

    return render(request, 'competitions/make_prediction.html', {'form': form, 'match': match})

@login_required
def make_prediction(request, match_id):
    match = Match.objects.get(id=match_id)
    
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction_data = form.save(commit=False)
            prediction_data.user = request.user
            prediction_data.match = match

            # Attempt to get an existing prediction, but handle duplicates gracefully
            predictions = Prediction.objects.filter(user=request.user, match=match)
            
            if predictions.exists():
                messages.error(request, 'You have already made a prediction for this match.')
            else:
                try:
                    prediction_data.save()
                    messages.success(request, 'Your prediction has been submitted.')
                except IntegrityError:
                    messages.error(request, 'There was an error saving your prediction. Please try again.')
            
            return redirect('/')
    else:
        form = PredictionForm()

    return render(request, 'competitions/make_prediction.html', {'form': form, 'match': match})

@login_required
def calculate_results(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    matches = competition.match_set.all()
    users = set(Prediction.objects.filter(match__in=matches).values_list('user', flat=True))

    results = []
    for user in users:
        total_points = 0
        golden_goal_diff = float('inf')
        for match in matches:
            prediction = Prediction.objects.filter(match=match, user=user).first()
            if prediction:
                total_points += prediction.calculate_points()
                goal_diff = abs(prediction.golden_goal - match.golden_goal_time())
                golden_goal_diff = min(golden_goal_diff, goal_diff)

        CompetitionResult.objects.update_or_create(
            competition=competition,
            user_id=user,
            defaults={'total_points': total_points, 'golden_goal_difference': golden_goal_diff}
        )

    return redirect('/')


def leaderboardold(request):
    competition = get_object_or_404(Competition, id=competition_id)
    results = CompetitionResult.objects.filter(competition=competition).order_by('-total_points', 'golden_goal_difference')
    return render(request, 'competitions/leaderboard.html', {'competition': competition, 'results': results})


@login_required
def leaderboardold2(request):
    users = User.objects.all()
    leaderboard_data = []

    for user in users:
        predictions = Prediction.objects.filter(user=user)
        
        total_points = sum(prediction.get_points() for prediction in predictions)
        golden_goal_difference = min(abs(prediction.golden_goal - prediction.match.first_goal_time) for prediction in predictions)

        leaderboard_data.append({
            'user': user,
            'total_points': total_points,
            'golden_goal_difference': golden_goal_difference,
            })
    # Sort users by total points (descending) and then by golden goal difference (ascending)
    leaderboard_data.sort(key=lambda x: (-x['total_points'], x['golden_goal_difference']))

    context = {
        'leaderboard_data': leaderboard_data,
    }
    return render(request, 'competitions/leaderboard.html', context)


# New leaderboard

def calculate_points(prediction):
    # Calculate points based on your business logic
    if (prediction.predicted_home_team_score == prediction.match.home_team_score and
            prediction.predicted_away_team_score == prediction.match.away_team_score):
        return 6
    elif ((prediction.predicted_home_team_score > prediction.predicted_away_team_score and
           prediction.match.home_team_score > prediction.match.away_team_score) or
          (prediction.predicted_home_team_score < prediction.predicted_away_team_score and
           prediction.match.home_team_score < prediction.match.away_team_score) or
          (prediction.predicted_home_team_score == prediction.predicted_away_team_score and
           prediction.match.home_team_score == prediction.match.away_team_score)):
        return 4
    else:
        return 0
@login_required
def leaderboardold3(request):
    users_with_data = []
    users = Prediction.objects.values('user').distinct()

    for user in users:
        predictions = Prediction.objects.filter(user=user['user'])
        #predictions = Prediction.objects.filter(user=user)
        if predictions.exists():
            total_points = sum(calculate_points(prediction) for prediction in predictions)
            # Assuming golden goal difference is already calculated and stored in each Prediction
            # golden_goal_diff = min(abs(prediction.golden_goal - prediction.match.first_goal_time) for prediction in predictions)
            golden_goal_diff = min(abs(prediction.golden_goal - prediction.match.first_goal_time) for prediction in predictions)
            if total_points > 0:
                users_with_data.append({
                    'user': predictions[0].user,
                    'total_points': total_points,
                    'golden_goal_diff': golden_goal_diff,
                })

    sorted_leaderboard = sorted(users_with_data, key=lambda x: (-x['total_points'], x['golden_goal_diff']))


    return render(request, 'competitions/leaderboard.html', {'leaderboard_data': sorted_leaderboard})

@login_required
def leaderboardnew(request, pk):
    # Get the competition, or use a default if none is provided
    # competition = get_object_or_404(Competition, id=competition_id)
    competition = Competition.objects.get(pk=pk)

    

    # Filter predictions for the specified competition
    predictions = Prediction.objects.filter(match__competition=competition)

    # Create a dictionary to store total points and golden goal differences
    user_data = {}
    
    for prediction in predictions:
        user = prediction.user
        
        if user not in user_data:
            user_data[user] = {
                'total_points': 0,
                'golden_goal_diff': float('inf')  # Initialize with a large value
            }

        total_points = calculate_points(prediction)
        user_data[user]['total_points'] += total_points
        
        # Update golden goal difference if applicable
        match = prediction.match
        if match.first_goal_time is not None:
            golden_goal_diff = abs(prediction.golden_goal - match.first_goal_time)
            user_data[user]['golden_goal_diff'] = min(user_data[user]['golden_goal_diff'], golden_goal_diff)

    # Convert user data dictionary to a list and sort
    users_with_data = [
        {'user': user, **data}
        for user, data in user_data.items()
        if data['total_points'] > 0
    ]
    
    sorted_leaderboard = sorted(users_with_data, key=lambda x: (-x['total_points'], x['golden_goal_diff']))

    return render(request, 'competitions/leaderboard.html', 
        {'leaderboard_data': sorted_leaderboard, 'competition': competition})

@login_required
def leaderboardold7(request, competition_id):
    # Get the specific competition by its ID
    competition = get_object_or_404(Competition, id=competition_id)

    # Annotate users with their total points and golden goal difference for this competition
    users_with_data = (
        Prediction.objects.filter(match__competition=competition)
        .values('user__username')
        .annotate(
            total_points=Coalesce(Sum('points'), Value(0)),
            golden_goal_diff=Min(
                Coalesce(
                    F('golden_goal') - F('match__first_goal_time'),
                    Value(float('inf'))
                )
            )
        )
        .order_by('-total_points', 'golden_goal_diff')
    )

    return render(request, 'competitions/leaderboard.html', {
        'leaderboard_data': users_with_data,
        'competition': competition
    })

@login_required
def leaderboardold8(request, competition_id):
    # Get the specific competition by its ID
    competition = get_object_or_404(Competition, id=competition_id)

    # Get all predictions for the competition
    predictions = Prediction.objects.filter(match__competition=competition)

    # Dictionary to hold user data
    user_data = {}

    for prediction in predictions:
        user = prediction.user
        
        if user not in user_data:
            user_data[user] = {
                'total_points': 0,
                'golden_goal_diff': float('inf')  # Initialize with a large value
            }

        # Calculate points for the current prediction
        points = calculate_points(prediction)
        user_data[user]['total_points'] += points

        # Calculate golden goal difference
        if prediction.match.first_goal_time is not None:
            golden_goal_diff = abs(prediction.golden_goal - prediction.match.first_goal_time)
            user_data[user]['golden_goal_diff'] = min(user_data[user]['golden_goal_diff'], golden_goal_diff)

    # Convert the user_data dictionary to a list and sort it
    sorted_leaderboard = sorted(user_data.items(), key=lambda x: (-x[1]['total_points'], x[1]['golden_goal_diff']))

    return render(request, 'competitions/leaderboard.html', {
        'leaderboard_data': sorted_leaderboard,
        'competition': competition
    })

class LeaderboardEntry:
    def __init__(self, user, total_points, golden_goal_diff):
        self.user = user
        self.total_points = total_points
        self.golden_goal_diff = golden_goal_diff

@login_required
def leaderboard(request, competition_id):
    # Get the specific competition by its ID
    competition = get_object_or_404(Competition, id=competition_id)

    # Get all predictions for the competition
    predictions = Prediction.objects.filter(match__competition=competition)

    # Dictionary to hold user data
    user_data = {}

    for prediction in predictions:
        user = prediction.user
        
        if user not in user_data:
            user_data[user] = {
                'total_points': 0,
                'golden_goal_diff': float('inf')  # Initialize with a large value
            }

        # Calculate points for the current prediction
        points = calculate_points(prediction)
        user_data[user]['total_points'] += points

        # Calculate golden goal difference
        if prediction.match.first_goal_time is not None:
            golden_goal_diff = abs(prediction.golden_goal - prediction.match.first_goal_time)
            user_data[user]['golden_goal_diff'] = min(user_data[user]['golden_goal_diff'], golden_goal_diff)

    # Convert the user_data dictionary to a list of LeaderboardEntry objects
    leaderboard_objects = [
        LeaderboardEntry(user=user, total_points=data['total_points'], golden_goal_diff=data['golden_goal_diff'])
        for user, data in user_data.items()
    ]

    # Sort the leaderboard_objects
    sorted_leaderboard = sorted(leaderboard_objects, key=lambda x: (-x.total_points, x.golden_goal_diff))

    print(type(sorted_leaderboard))

    return render(request, 'competitions/leaderboard.html', {
        'leaderboard_data': sorted_leaderboard,
        'competition': competition
    })


@login_required
def user_detail(request, user_id):
    # competition = get_object_or_404(Competition, id=competition_id)
    # Get all predictions for the competition
    # predictions = Prediction.objects.filter(user=user, match__competition=competition)
    user = get_object_or_404(User, pk=user_id)
    predictions = Prediction.objects.filter(user=user).select_related('match__competition')
    total_points = sum(calculate_points(prediction) for prediction in predictions)
    
    # Group predictions by competition
    competitions = {}
    for prediction in predictions:
        comp = prediction.match.competition
        if comp not in competitions:
            competitions[comp] = []
        competitions[comp].append(prediction)

    context = {
        'user': user,
        'competitions': competitions,
        'total_points': total_points,
    }
    return render(request, 'competitions/user_detail.html', context)




