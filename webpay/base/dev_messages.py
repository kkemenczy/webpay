from django.conf import settings

from tower import ugettext as _


BAD_JWT_ISSUER = 'BAD_JWT_ISSUER'
BAD_ICON_KEY = 'BAD_ICON_KEY'
BAD_PRICE_POINT = 'BAD_PRICE_POINT'
BAD_SIM_RESULT = 'BAD_SIM_RESULT'
EXPIRED_JWT = 'EXPIRED_JWT'
INVALID_JWT = 'INVALID_JWT'
INVALID_JWT_OBJ = 'INVALID_JWT_OBJ'
JWT_DECODE_ERR = 'JWT_DECODE_ERR'
MALFORMED_URL = 'MALFORMED_URL'
NO_DEFAULT_LOC = 'NO_DEFAULT_LOC'
NO_SIM_REASON = 'NO_SIM_REASON'
SIM_DISABLED = 'SIM_DISABLED'
SIM_ONLY_KEY = 'SIM_ONLY_KEY'

SHORT_FIELDS = ('chargebackURL',
                'defaultLocale',
                'id',
                'name',
                'postbackURL',
                'productData')

# Map of field name to 'too long' error code.
SHORT_FIELD_TOO_LONG_CODE = {}

# Convert all short fields into error codes.
# E.G. CHARGEBACKURL_TOO_LONG
for fn in SHORT_FIELDS:
    cd = '{0}_TOO_LONG'.format(fn.upper())
    SHORT_FIELD_TOO_LONG_CODE[fn] = cd


def legend():
    """
    Legend of error message codes for developers.

    These codes are used in validation but will be slightly hidden from users
    so as not to cause confusion. The legend is a reference for
    developers.
    """
    _legend = {
        BAD_ICON_KEY:
            # L10n: First argument is an example of the proper key format.
            _('An image icon key was not an object. Correct example: {0}')
            .format('{"64": "https://.../icon_64.png"}'),
        # L10n: JWT stands for JSON Web Token and does not need to be
        # localized.
        BAD_JWT_ISSUER: _('No one has been registered for this JWT issuer.'),
        BAD_PRICE_POINT: _('The price point is unknown or invalid.'),
        BAD_SIM_RESULT:
            _('The requested payment simulation result is not supported.'),
        # L10n: JWT stands for JSON Web Token and does not need to be
        # localized.
        EXPIRED_JWT: _('The JWT has expired.'),
        INVALID_JWT:
            # L10n: JWT stands for JSON Web Token and does not need to be
            # localized.
            _('The JWT signature is invalid or the JWT is malformed.'),
        # L10n: JWT stands for JSON Web Token and does not need to be
        # localized.
        INVALID_JWT_OBJ: _('The JWT did not decode to a JSON object.'),
        # L10n: JWT stands for JSON Web Token and does not need to be
        # localized.
        JWT_DECODE_ERR: _('Error decoding JWT.'),
        # L10n: 'postback' is a term that means a URL accepting HTTP posts.
        MALFORMED_URL: _('A URL is malformed. This could be a postback '
                         'URL or an icon URL.'),
        NO_DEFAULT_LOC:
            # L10n: First and second arguements are the names of keys.
            _('If {0} is defined, then you must also define {1}.')
            .format('locales', 'defaultLocale'),
        NO_SIM_REASON:
            # L10n: First argument is the name of the key, 'reason'.
            _("The requested chargeback simulation is missing "
              "the key '{0}'.").format('reason'),
        SIM_DISABLED: _('Payment simulations are disabled at this time.'),
        SIM_ONLY_KEY:
            _('This payment key can only be used to simulate purchases.'),
    }

    # Define all short field too long errors.
    for field, key in SHORT_FIELD_TOO_LONG_CODE.iteritems():
        # L10n: First argument is the name of a key. Second
        # argument is a number.
        _legend[key] = _('The value for key "{0}" exceeds the maximum '
                         'length of {1}').format(
                                field, settings.SHORT_FIELD_MAX_LENGTH)

    return _legend
