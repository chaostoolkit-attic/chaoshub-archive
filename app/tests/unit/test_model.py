# -*- coding: utf-8 -*-
from flask import Flask
import pytest

from chaoshubdashboard.model import get_user_info_secret_key


def test_get_user_info_secret_key(app: Flask):
    with app.app_context():
        assert get_user_info_secret_key() == "whatever"


def test_get_user_info_secret_key_requires_key_to_be_set(app: Flask):
    with app.app_context():
        app.config.pop("USER_PROFILE_SECRET_KEY", None)
        with pytest.raises(RuntimeError) as x:
            get_user_info_secret_key()
        assert "User profile secret key not set!" in str(x)
