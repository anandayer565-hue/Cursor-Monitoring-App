"""WTForms with CSRF (Flask-WTF)."""

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

from app.validators import is_localhost_host


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(max=64)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(max=256)],
    )
    submit = SubmitField("Sign in")


class LogoutForm(FlaskForm):
    submit = SubmitField("Sign out")


class ServerForm(FlaskForm):
    display_name = StringField(
        "Display name",
        validators=[DataRequired(), Length(max=120)],
    )
    hostname = StringField(
        "Hostname / IP",
        validators=[DataRequired(), Length(max=255)],
        default="127.0.0.1",
    )
    ssh_port = IntegerField(
        "SSH port",
        validators=[DataRequired(), NumberRange(min=1, max=65535)],
        default=22,
    )
    ssh_username = StringField(
        "SSH username",
        validators=[DataRequired(), Length(max=64)],
    )
    ssh_password = PasswordField(
        "SSH password",
        validators=[Optional(), Length(max=256)],
    )
    ssh_key_path = StringField(
        "SSH key path",
        validators=[Optional(), Length(max=512)],
    )
    submit = SubmitField("Add server")

    def validate_hostname(self, field):
        if not is_localhost_host(field.data or ""):
            raise ValidationError(
                "Demo allows localhost / 127.0.0.1 / ::1 only."
            )

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators=extra_validators)
        password = (self.ssh_password.data or "").strip()
        key_path = (self.ssh_key_path.data or "").strip()
        if not password and not key_path:
            self.ssh_password.errors.append(
                "Provide an SSH password or a key path."
            )
            ok = False
        return ok


class RefreshForm(FlaskForm):
    submit = SubmitField("Refresh")
