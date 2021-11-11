# Generated by Django 3.2.8 on 2021-11-11 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20211108_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockanalysis',
            name='negativeSentiment',
        ),
        migrations.RemoveField(
            model_name='stockanalysis',
            name='positiveSentiment',
        ),
        migrations.AddField(
            model_name='stockanalysis',
            name='numNegativeTweets',
            field=models.IntegerField(default=0, verbose_name='Number of Positive Tweets'),
        ),
        migrations.AddField(
            model_name='stockanalysis',
            name='numNeutralTweets',
            field=models.IntegerField(default=0, verbose_name='Number of Positive Tweets'),
        ),
        migrations.AddField(
            model_name='stockanalysis',
            name='numPositiveTweets',
            field=models.IntegerField(default=0, verbose_name='Number of Positive Tweets'),
        ),
        migrations.AddField(
            model_name='stockanalysis',
            name='sentimentScore',
            field=models.IntegerField(default=0, verbose_name='Sentiment'),
        ),
    ]