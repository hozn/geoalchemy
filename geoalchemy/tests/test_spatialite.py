from unittest import TestCase
from binascii import b2a_hex
from sqlalchemy import (create_engine, MetaData, Column, Integer, String,
        Numeric, func, literal, select)
from sqlalchemy.orm import sessionmaker, column_property
from sqlalchemy.exc import NotSupportedError
from sqlalchemy.ext.declarative import declarative_base

from pysqlite2 import dbapi2 as sqlite
from geoalchemy.geometry import (Geometry, GeometryColumn, Point, Polygon,
		LineString, GeometryDDL, WKTSpatialElement)
from nose.tools import ok_, eq_, raises


engine = create_engine('sqlite://', module=sqlite, echo=True)
connection = engine.raw_connection().connection
connection.enable_load_extension(True)
metadata = MetaData(engine)
session = sessionmaker(bind=engine)()
session.execute("select load_extension('/usr/local/lib/libspatialite.so')")
session.execute("SELECT InitSpatialMetaData()")
session.commit()
Base = declarative_base(metadata=metadata)

class Road(Base):
    __tablename__ = 'roads'

    road_id = Column(Integer, primary_key=True)
    road_name = Column(String)
    road_geom = GeometryColumn(LineString(2, srid=4326), sfs=True)

class Lake(Base):
    __tablename__ = 'lakes'

    lake_id = Column(Integer, primary_key=True)
    lake_name = Column(String)
    lake_geom = GeometryColumn(Polygon(2, srid=4326))

class Spot(Base):
    __tablename__ = 'spots'

    spot_id = Column(Integer, primary_key=True)
    spot_height = Column(Numeric)
    spot_location = GeometryColumn(Point(2, srid=4326))

# enable the DDL extension, which allows CREATE/DROP operations
# to work correctly.  This is not needed if working with externally
# defined tables.    
GeometryDDL(Road.__table__)
GeometryDDL(Lake.__table__)
GeometryDDL(Spot.__table__)

class TestGeometry(TestCase):

    def setUp(self):

        metadata.drop_all()
        session.execute("DROP VIEW geom_cols_ref_sys")
        session.execute("DROP TABLE geometry_columns")
        session.execute("DROP TABLE spatial_ref_sys")
        session.commit()
        session.execute("SELECT InitSpatialMetaData()")
        session.execute("INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, ref_sys_name, proj4text) VALUES (4326, 'epsg', 4326, 'WGS 84', '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')")
        metadata.create_all()

        # Add objects.  We can use strings...
        session.add_all([
            Road(road_name='Jeff Rd', road_geom='LINESTRING(-88.9139332929936 42.5082802993631,-88.8203027197452 42.5985669235669,-88.7383759681529 42.7239650127389,-88.6113059044586 42.9680732929936,-88.3655256496815 43.1402866687898)'),
            Road(road_name='Peter Rd', road_geom='LINESTRING(-88.9139332929936 42.5082802993631,-88.8203027197452 42.5985669235669,-88.7383759681529 42.7239650127389,-88.6113059044586 42.9680732929936,-88.3655256496815 43.1402866687898)'),
            Road(road_name='Geordie Rd', road_geom='LINESTRING(-89.2232485796178 42.6420382611465,-89.2449842484076 42.9179140573248,-89.2316084522293 43.106847178344,-89.0710987261147 43.243949044586,-89.092834566879 43.2957802993631,-89.092834566879 43.2957802993631,-89.0309715095541 43.3175159681529)'),
            Road(road_name='Paul St', road_geom='LINESTRING(-88.2652071783439 42.5584395350319,-88.1598727834395 42.6269904904459,-88.1013536751592 42.621974566879,-88.0244428471338 42.6437102356688,-88.0110670509554 42.6771497261147)'),
            Road(road_name='Graeme Ave', road_geom='LINESTRING(-88.5477708726115 42.6988853949045,-88.6096339299363 42.9697452675159,-88.6029460318471 43.0884554585987,-88.5912422101911 43.187101955414)'),
            Road(road_name='Phil Tce', road_geom='LINESTRING(-88.9356689617834 42.9363057770701,-88.9824842484076 43.0366242484076,-88.9222931656051 43.1085191528662,-88.8487262866242 43.0449841210191)'),
            Lake(lake_name='My Lake', lake_geom='POLYGON((-88.7968950764331 43.2305732929936,-88.7935511273885 43.1553344394904,-88.716640299363 43.1570064140127,-88.7250001719745 43.2339172420382,-88.7968950764331 43.2305732929936))'),
            Lake(lake_name='Lake White', lake_geom='POLYGON((-88.1147292993631 42.7540605095542,-88.1548566878981 42.7824840764331,-88.1799363057325 42.7707802547771,-88.188296178344 42.7323248407643,-88.1832802547771 42.6955414012739,-88.1565286624204 42.6771496815287,-88.1448248407643 42.6336783439491,-88.131449044586 42.5718152866242,-88.1013535031847 42.565127388535,-88.1080414012739 42.5868630573248,-88.1164012738854 42.6119426751592,-88.1080414012739 42.6520700636943,-88.0980095541401 42.6838375796178,-88.0846337579618 42.7139331210191,-88.1013535031847 42.7423566878981,-88.1147292993631 42.7540605095542))'),
            Lake(lake_name='Lake Blue', lake_geom='POLYGON((-89.0694267515924 43.1335987261147,-89.1078821656051 43.1135350318471,-89.1329617834395 43.0884554140127,-89.1312898089172 43.0466560509554,-89.112898089172 43.0132165605096,-89.0694267515924 42.9898089171975,-89.0343152866242 42.953025477707,-89.0209394904459 42.9179140127389,-89.0042197452229 42.8961783439491,-88.9774681528663 42.8644108280255,-88.9440286624204 42.8292993630573,-88.9072452229299 42.8142515923567,-88.8687898089172 42.815923566879,-88.8687898089172 42.815923566879,-88.8102707006369 42.8343152866242,-88.7734872611465 42.8710987261147,-88.7517515923567 42.9145700636943,-88.7433917197452 42.9730891719745,-88.7517515923567 43.0299363057325,-88.7734872611465 43.0867834394905,-88.7885352038217 43.158678388535,-88.8738057324841 43.1620222929936,-88.947372611465 43.1937898089172,-89.0042197452229 43.2138535031847,-89.0410031847134 43.2389331210191,-89.0710987261147 43.243949044586,-89.0660828025478 43.2238853503185,-89.0543789808917 43.203821656051,-89.0376592356688 43.175398089172,-89.0292993630573 43.1519904458599,-89.0376592356688 43.1369426751592,-89.0393312101911 43.1386146496815,-89.0393312101911 43.1386146496815,-89.0510350318471 43.1335987261147,-89.0694267515924 43.1335987261147))'),
            Lake(lake_name='Lake Deep', lake_geom='POLYGON((-88.9122611464968 43.038296178344,-88.9222929936306 43.0399681528663,-88.9323248407643 43.0282643312102,-88.9206210191083 43.0182324840764,-88.9105891719745 43.0165605095542,-88.9005573248408 43.0232484076433,-88.9072452229299 43.0282643312102,-88.9122611464968 43.038296178344))'),
            Spot(spot_height=420.40, spot_location='POINT(-88.5945861592357 42.9480095987261)'),
            Spot(spot_height=102.34, spot_location='POINT(-88.9055734203822 43.0048567324841)'),
            Spot(spot_height=388.62, spot_location='POINT(-89.201512910828 43.1051752038217)'),
            Spot(spot_height=454.66, spot_location='POINT(-88.3304141847134 42.6269904904459)'),
        ])

        # or use an explicit WKTSpatialElement (similar to saying func.GeomFromText())
        self.r = Road(road_name='Dave Cres', road_geom=WKTSpatialElement('LINESTRING(-88.6748409363057 43.1035032292994,-88.6464173694267 42.9981688343949,-88.607961955414 42.9680732929936,-88.5160033566879 42.9363057770701,-88.4390925286624 43.0031847579618)', 4326))
        session.add(self.r)
        session.commit()

    def tearDown(self):
        session.rollback()
        metadata.drop_all()

    # Test Geometry Functions

    def test_wkt(self):
        eq_(session.scalar(self.r.road_geom.wkt), 'LINESTRING(-88.674841 43.103503, -88.646417 42.998169, -88.607962 42.968073, -88.516003 42.936306, -88.439093 43.003185)')

    def test_wkb(self):
        eq_(b2a_hex(session.scalar(self.r.road_geom.wkb)).upper(), '010200000005000000D7DB0998302B56C0876F04983F8D45404250F5E65E2956C068CE11FFC37F4540C8ED42D9E82656C0EFC45ED3E97B45407366F132062156C036C921DED877454078A18C171A1C56C053A5AF5B68804540')

    def test_persistent(self):
        eq_(b2a_hex(session.scalar(self.r.road_geom.wkb)).upper(), '010200000005000000D7DB0998302B56C0876F04983F8D45404250F5E65E2956C068CE11FFC37F4540C8ED42D9E82656C0EFC45ED3E97B45407366F132062156C036C921DED877454078A18C171A1C56C053A5AF5B68804540')

    def test_svg(self):
        eq_(session.scalar(self.r.road_geom.svg), 'M -88.674841 -43.103503 -88.646417 -42.998169 -88.607962 -42.968073 -88.516003 -42.936306 -88.439093 -43.003185 ')

    def test_fgf(self):
        eq_(b2a_hex(session.scalar(self.r.road_geom.fgf())), '020000000100000005000000d7db0998302b56c0876f04983f8d454000000000000000004250f5e65e2956c068ce11ffc37f45400000000000000000c8ed42d9e82656c0efc45ed3e97b454000000000000000007366f132062156c036c921ded8774540000000000000000078a18c171a1c56c053a5af5b688045400000000000000000')

    def test_dimension(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        eq_(session.scalar(l.lake_geom.dimension), 2)
        eq_(session.scalar(r.road_geom.dimension), 1)
        eq_(session.scalar(s.spot_location.dimension), 0)

    def test_srid(self):
        eq_(session.scalar(self.r.road_geom.srid), 4326)

    def test_geometry_type(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        eq_(session.scalar(l.lake_geom.geometry_type), 'POLYGON')
        eq_(session.scalar(r.road_geom.geometry_type), 'LINESTRING')
        eq_(session.scalar(s.spot_location.geometry_type), 'POINT')

    def test_is_empty(self):
        ok_(not session.scalar(self.r.road_geom.is_empty))

    def test_is_simple(self):
        ok_(session.scalar(self.r.road_geom.is_simple))

    def test_is_valid(self):
        assert session.scalar(self.r.road_geom.is_valid)

    def test_boundary(self):
        eq_(b2a_hex(session.scalar(self.r.road_geom.boundary)), '0001e6100000d7db0998302b56c053a5af5b6880454078a18c171a1c56c0876f04983f8d45407c04000000020000006901000000d7db0998302b56c0876f04983f8d4540690100000078a18c171a1c56c053a5af5b68804540fe')

    def test_envelope(self):
        eq_(b2a_hex(session.scalar(self.r.road_geom.envelope)), '0001ffffffffd7db0998302b56c036c921ded877454078a18c171a1c56c0876f04983f8d45407c030000000100000005000000d7db0998302b56c036c921ded877454078a18c171a1c56c036c921ded877454078a18c171a1c56c0876f04983f8d4540d7db0998302b56c0876f04983f8d4540d7db0998302b56c036c921ded8774540fe')

    def test_x(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_( not session.scalar(l.lake_geom.x))
        ok_( not session.scalar(r.road_geom.x))
        eq_(session.scalar(s.spot_location.x), -88.594586159235703)

    def test_y(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(not session.scalar(l.lake_geom.y))
        ok_(not session.scalar(r.road_geom.y))
        eq_(session.scalar(s.spot_location.y), 42.948009598726102)

    def test_start_point(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(not session.scalar(l.lake_geom.start_point))
        eq_(b2a_hex(session.scalar(r.road_geom.start_point)), '0001ffffffff850811e27d3a56c0997b2f540f414540850811e27d3a56c0997b2f540f4145407c01000000850811e27d3a56c0997b2f540f414540fe')
        ok_(not session.scalar(s.spot_location.start_point))

    def test_end_point(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(not session.scalar(l.lake_geom.end_point))
        eq_(b2a_hex(session.scalar(r.road_geom.end_point)), '0001ffffffffccceb1c5641756c02c42dfe9f4914540ccceb1c5641756c02c42dfe9f49145407c01000000ccceb1c5641756c02c42dfe9f4914540fe')
        ok_(not session.scalar(s.spot_location.end_point))

    def test_length(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        eq_(session.scalar(l.lake_geom.length), 0.30157858985653774)
        eq_(session.scalar(r.road_geom.length), 0.8551694164147895)
        ok_(not session.scalar(s.spot_location.length))

    def test_is_closed(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(not session.scalar(l.lake_geom.is_closed))
        ok_(not session.scalar(r.road_geom.is_closed))
        ok_(not session.scalar(s.spot_location.is_closed))

    def test_is_ring(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(session.scalar(l.lake_geom.is_ring))
        ok_(not session.scalar(r.road_geom.is_ring))
        ok_(session.scalar(s.spot_location.is_ring))

    def test_num_points(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(not session.scalar(l.lake_geom.num_points))
        eq_(session.scalar(r.road_geom.num_points), 5)
        ok_(not session.scalar(s.spot_location.num_points))

    def test_point_n(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        ok_(not session.scalar(l.lake_geom.point_n()))
        eq_(b2a_hex(session.scalar(r.road_geom.point_n(5))), '0001ffffffffccceb1c5641756c02c42dfe9f4914540ccceb1c5641756c02c42dfe9f49145407c01000000ccceb1c5641756c02c42dfe9f4914540fe')
        ok_(not session.scalar(s.spot_location.point_n()))

    def test_centroid(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        eq_(b2a_hex(session.scalar(l.lake_geom.centroid)), '0001ffffffff81ec9573803056c04bc4995bce98454081ec9573803056c04bc4995bce9845407c0100000081ec9573803056c04bc4995bce984540fe')
        eq_(b2a_hex(session.scalar(r.road_geom.centroid)), '0001ffffffff1cecabbd0b2a56c022b0f465cd6b45401cecabbd0b2a56c022b0f465cd6b45407c010000001cecabbd0b2a56c022b0f465cd6b4540fe')
        ok_(b2a_hex(session.scalar(s.spot_location.centroid)), '0001ffffffff95241bb30d2656c04e69e7605879454095241bb30d2656c04e69e760587945407c0100000095241bb30d2656c04e69e76058794540fe')

    def test_area(self):
        l = session.query(Lake).get(1)
        r = session.query(Road).get(1)
        s = session.query(Spot).get(1)
        eq_(session.scalar(l.lake_geom.area), 0.0056748625704927669)
        eq_(session.scalar(r.road_geom.area), 0.0)
        eq_(session.scalar(s.spot_location.area), 0.0)

    # Test Geometry Relations

    def test_crosses(self):
        r1 = session.query(Road).filter(Road.road_name=='Graeme Ave').one()
        eq_([(r.road_name, session.scalar(r.road_geom.wkt)) for r in session.query(Road).filter(Road.road_geom.crosses(r1.road_geom)).all()], [(u'Jeff Rd', u'LINESTRING(-88.913933 42.50828, -88.820303 42.598567, -88.738376 42.723965, -88.611306 42.968073, -88.365526 43.140287)'), (u'Peter Rd', u'LINESTRING(-88.913933 42.50828, -88.820303 42.598567, -88.738376 42.723965, -88.611306 42.968073, -88.365526 43.140287)'), (u'Dave Cres', u'LINESTRING(-88.674841 43.103503, -88.646417 42.998169, -88.607962 42.968073, -88.516003 42.936306, -88.439093 43.003185)')])
