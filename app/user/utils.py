from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(data):

        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()

    @staticmethod
    def normalize_email(email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email
