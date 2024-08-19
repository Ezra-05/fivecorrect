from django.db import models
from django.conf import settings
from django.utils import timezone  # Import timezone

class Competition(models.Model):
    name = models.CharField(max_length=100)
    published_date = models.DateField()
    start_time = models.DateTimeField(blank=True, null=True)  # Add start_time for the competition

    def update_start_time(self):
        # Update the competition's start_time to the earliest match start_time
        earliest_match = self.match_set.order_by('start_time').first()
        if earliest_match:
            self.start_time = earliest_match.start_time
            self.save()

    def __str__(self):
        return self.name

class Match(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_team_score = models.IntegerField(default=0)
    away_team_score = models.IntegerField(default=0)
    start_time = models.DateTimeField(default=timezone.now)  # Temporarily provide a default value
    # Add a field to store the minute of the first goal
    first_goal_time = models.IntegerField(default=0)  # Assuming minute of first goal is stored here

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    def golden_goal_time(self):
        # Return the minute of the first goal
        return self.first_goal_time if self.first_goal_time is not None else 0

class Prediction(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    predicted_home_team_score = models.IntegerField()
    predicted_away_team_score = models.IntegerField()
    golden_goal = models.IntegerField()

    def calculate_points(self):
        if self.match.home_team_score == self.predicted_home_team_score and self.match.away_team_score == self.predicted_away_team_score:
            return 6
        elif ((self.match.home_team_score > self.match.away_team_score and self.predicted_home_team_score > self.predicted_away_team_score) or
              (self.match.home_team_score < self.match.away_team_score and self.predicted_home_team_score < self.predicted_away_team_score) or
              (self.match.home_team_score == self.match.away_team_score and self.predicted_home_team_score == self.predicted_away_team_score)):
            return 4
        else:
            return 0

    def __str__(self):
        return f"{self.user.username}'s prediction for {self.match}"

    def get_points(self):
        if self.match.home_team_score == self.predicted_home_team_score and self.match.away_team_score == self.predicted_away_team_score:
            return 6
        elif ((self.match.home_team_score > self.match.away_team_score and self.predicted_home_team_score > self.predicted_away_team_score) or
              (self.match.home_team_score < self.match.away_team_score and self.predicted_home_team_score < self.predicted_away_team_score) or
              (self.match.home_team_score == self.match.away_team_score and self.predicted_home_team_score == self.predicted_away_team_score)):
            return 4
        else:
            return 0
    class Meta:
        unique_together = ('user', 'match')

class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.IntegerField()
    golden_goal_difference = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.competition.name} result"
