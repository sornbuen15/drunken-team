import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from drunken_team.models.base import Base
from drunken_team.models.tenant import Customer
from drunken_team.models.device import Device
from drunken_team.models.subscription import SubscriptionService


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_customer_creation(db_session):
    customer = Customer(name="Test Corp", email="test@test.com")
    db_session.add(customer)
    db_session.commit()

    saved = db_session.query(Customer).filter_by(email="test@test.com").first()
    assert saved is not None
    assert saved.name == "Test Corp"


def test_device_creation_linked_to_customer(db_session):
    customer = Customer(name="Device Corp", email="device@test.com")
    db_session.add(customer)
    db_session.flush()

    device = Device(customer_id=customer.id, node_uuid="uuid-1234", name="Sensor 1")
    db_session.add(device)
    db_session.commit()

    saved_device = db_session.query(Device).filter_by(node_uuid="uuid-1234").first()
    assert saved_device is not None
    assert saved_device.customer.name == "Device Corp"


def test_subscription_creation_linked_to_customer(db_session):
    customer = Customer(name="Sub Corp", email="sub@test.com")
    db_session.add(customer)
    db_session.flush()

    sub = SubscriptionService(customer_id=customer.id, plan_name="Pro")
    db_session.add(sub)
    db_session.commit()

    saved_sub = db_session.query(SubscriptionService).filter_by(plan_name="Pro").first()
    assert saved_sub is not None
    assert saved_sub.customer.name == "Sub Corp"
