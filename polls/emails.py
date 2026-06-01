"""
Email utility functions for the voting system.
Sends voter credentials and election invitations.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


def send_voter_credentials_email(voter, password):

    """
    Send login credentials to a newly registered voter.
    
    Args:
        voter: PoliceUser instance
        password: Plain text password for the voter
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not voter.email:
        logger.warning(f"Cannot send credentials email to {voter.username} - no email address")
        return False
    
    subject = "Your VotingHub Voting System Login Credentials"

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    login_path = getattr(settings, 'LOGIN_URL', '/polls/login/')
    login_url = f"{site_url}{login_path}"

    message = f"""Hello {voter.get_full_name()},

You have been registered as a voter in the VotingHub Voting System.

Your login credentials are:

Username: {voter.username}
Password: {password}

Please login at your earliest and change your password.

Login URL: {login_url}

Important:
- Your username is your Force Number: {voter.force_number}
- You must change your password on first login
- Forgot your password? Use the "Forgot Password" link on the login page to reset it
- Contact your administrator if you need assistance

Best regards,
VotingHub System Administration
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[voter.email],
            fail_silently=False,
        )
        logger.info(f"Credentials email sent to {voter.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send credentials email to {voter.email}: {str(e)}")
        return False


def send_election_invitation_email(voter, election, password=None):
    """
    Send election invitation to a voter.
    
    Args:
        voter: PoliceUser instance
        election: Election instance
        password: Optional plain text password to include in the email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not voter.email:
        logger.warning(f"Cannot send invitation email to {voter.username} - no email address")
        return False
    
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    login_path = getattr(settings, 'LOGIN_URL', '/polls/login/')
    login_url = f"{site_url}{login_path}"
    
    subject = f"Invitation: {election.title}"
    
    message = f"""Hello {voter.get_full_name()},

You have been invited to participate in an upcoming election.

Election Details:
==================
Title: {election.title}
Description: {election.description or 'N/A'}
Start Time: {election.start_time.strftime('%Y-%m-%d %H:%M')}
End Time: {election.end_time.strftime('%Y-%m-%d %H:%M')}
Status: {election.status}

Positions:
"""
    
    # Add positions to the message
    positions = election.positions.all()
    if positions:
        for pos in positions:
            message += f"  - {pos.name}\n"
    else:
        message += "  - No positions available\n"
    
    message += f"""
Eligibility:
"""
    if election.eligible_ranks:
        message += f"  Ranks: {election.eligible_ranks}\n"
    if election.eligible_stations:
        message += f"  Stations: {election.eligible_stations}\n"
    
    message += f"""
Your login credentials:

Username: {voter.username}
"""
    if password:
        message += f"""Password: {password}
"""
    else:
        message += "Password: (Use the password sent in your registration email)\n"
    
    message += f"""
Please login and cast your vote before the election ends.

Login URL: {login_url}

Forgot your password? Use the "Forgot Password" link on the login page to reset it.

Best regards,
VotingHub System Administration
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[voter.email],
            fail_silently=False,
        )
        logger.info(f"Election invitation email sent to {voter.email} for election {election.title}")
        return True
    except Exception as e:
        logger.error(f"Failed to send invitation email to {voter.email}: {str(e)}")
        return False


def send_bulk_voter_credentials_email(voter, password, election_title=None):
    """
    Send credentials to a voter registered in bulk.
    Includes optional election info if provided.
    
    Args:
        voter: PoliceUser instance
        password: Plain text password
        election_title: Optional election title for context
        
    Returns:
        bool: True if email was sent successfully
    """
    if not voter.email:
        logger.warning(f"Cannot send bulk credentials email to {voter.username} - no email address")
        return False
    
    subject = "Your VotingHub Voting System Login Credentials"
    
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    login_path = getattr(settings, 'LOGIN_URL', '/polls/login/')
    login_url = f"{site_url}{login_path}"

    message = f"""Hello {voter.get_full_name()},

You have been registered as a voter in the VotingHub Voting System.

Your login credentials are:

Username: {voter.username}
Password: {password}
Force Number: {voter.force_number}
Rank: {voter.get_rank_display()}
Station: {voter.station}
"""
    
    if election_title:
        message += f"\nYou have been registered to vote in: {election_title}\n"
    
    message += f"""
Please login at your earliest and change your password.

Login URL: {login_url}

Important:
- Your username is your Force Number: {voter.force_number}
- You must change your password on first login
- Forgot your password? Use the "Forgot Password" link on the login page to reset it
- Contact your administrator if you need assistance

Best regards,
VotingHub System Administration
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[voter.email],
            fail_silently=False,
        )
        logger.info(f"Bulk credentials email sent to {voter.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send bulk credentials email to {voter.email}: {str(e)}")
        return False
