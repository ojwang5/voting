# Generated migration to add position to Vote and update unique constraint

from django.db import migrations, models
import django.db.models.deletion


def populate_vote_position(apps, schema_editor):
    """Populate position field on existing votes from their candidate's position."""
    Vote = apps.get_model('polls', 'Vote')
    for vote in Vote.objects.select_related('candidate__position').all():
        if vote.candidate and vote.candidate.position_id:
            vote.position_id = vote.candidate.position_id
            vote.save(update_fields=['position'])


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_alter_candidate_force_number_and_more'),
    ]

    operations = [
        # Step 1: Add position field as nullable
        migrations.AddField(
            model_name='vote',
            name='position',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='polls.position',
            ),
        ),
        # Step 2: Populate existing votes from candidate.position
        migrations.RunPython(populate_vote_position, migrations.RunPython.noop),
        # Step 3: Make position non-nullable
        migrations.AlterField(
            model_name='vote',
            name='position',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='polls.position',
            ),
        ),
        # Step 4: Update unique constraint
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together={('voter', 'election', 'position')},
        ),
    ]

