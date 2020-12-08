from postDB import Model, Column, types


class Asset(Model):
    """
    Asset class used in the CDN and Badge class.

    Database Attributes:
        Attributes stored in the `guilds` table.

        :param int id:              The asset ID.
        :param str name:            The asset name to be displayed on web-dashboard.
        :param str url_path:        The CDN path this Asset should be mapped to
        :param str type:            The type of asset this is; Badge|Avatar|Image
        :param str base64:          The base64 encoded version of the Asset (Instead of BLOB in db)

    """
    id = Column(types.Serial)
    name = Column(types.String(length=100), unique=True)
    url_path = Column(types.String, primary_key=True)
    type = Column(types.String, primary_key=True)
    base64 = Column(types.String)