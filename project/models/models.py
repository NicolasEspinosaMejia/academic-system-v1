from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, \
    event, inspect, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Query, synonym
from project.resources.utils.generals_utils import GeneralsUtils

Base = declarative_base()


class TimeStamp(types.TypeDecorator):
    impl = types.TIMESTAMP

    def process_result_value(self, value, dialect):
        return str(value) if value else None


@event.listens_for(Query, "before_compile", retval=True)
def before_compile(query):
    if query._execution_options.get("include_deleted", False):
        return query

    for ent in query.column_descriptions:
        entity = ent['entity']
        if entity is None:
            continue
        if getattr(inspect(entity), 'mapper') and hasattr(entity, 'is_active'):
            query = query.enable_assertions(False).filter(entity.is_active)

    return query


@event.listens_for(Base, 'load', propagate=True)
def load(obj, context):
    if not obj.is_active and not\
            context.query._execution_options.get('include_deleted', False):
        raise TypeError(f'Deleted object {obj} was loaded')


class MarketAgent(Base):
    __tablename__ = 'ms_agent_agt'
    __table_args__ = {'schema': 'MS'}

    id_agt = Column(Integer, primary_key=True)
    id_typeagent_obj = Column(Integer)
    identification_agt = Column(String(50))
    name_agt = Column(String(100))
    description_agt = Column(String(100))
    logo_agt = Column(String(150))
    network_operator_agt = Column(Boolean)
    system_operator_agt = Column(Boolean)
    address_agt = Column(String(100))
    city_agt = Column(String(100))
    postal_code_agt = Column(String(100))
    phone_agt = Column(String(100))
    email_agt = Column(String(100))
    website_agt = Column(String(500))
    enrollment_date_agt = Column(Date)
    retirement_date_agt = Column(Date)
    date_create = Column(Date)
    is_active_agt = Column(Boolean, default=True)
    owner_data = Column(String(50))
    user_create = Column(String(50))
    user_update = Column(String(50))

    is_active = synonym('is_active_agt')

    associations = relationship('AgentMetering', backref='agent')

    RULES = {
        'id': ['fixed'],
        'activity': ['required', 'fixed'],
        'code': ['min:1', 'max:30'],
        'name': ['required', 'min:1', 'max:50'],
        'networkOperator': ['boolean', 'fixed'],
        'systemOperator': ['boolean', 'fixed'],
        'address': ['min:5', 'max:40'],
        'city': ['min:1', 'max:30'],
        'postalCode': ['min:2', 'max:12'],
        'phone': ['min:7', 'max:30', 'pattern:^[0-9.+-]+$'],
        'email': ['pattern:' r'^[^. |]+@([^. |]+\.)+[^. |]+$'],
        'website': ['min:10', 'max:500'],
        'enrollmentDate': ['datetime:%Y-%m-%dT%H:%M:%S'],
        'retirementDate': ['datetime:%Y-%m-%dT%H:%M:%S'],
    }


class AgentMetering(Base):
    __tablename__ = 'ms_agent_metering_agm'
    __table_args__ = {'schema': 'MS'}

    id_agm = Column(Integer, primary_key=True)
    id_agt = Column(Integer, ForeignKey('MS.ms_agent_agt.id_agt'))
    id_spo = Column(Integer,
                    ForeignKey('MS.ms_service_point_spo.id_spo'))
    id_metering_type_dev = Column(
        Integer, ForeignKey('MS.ms_bridge_objets.id_obj'))
    is_active_agm = Column(Boolean, default=True)
    owner_data = Column(String)

    is_active = synonym('is_active_agm')


class BridgeObject(Base):
    __tablename__ = 'ms_bridge_objets'
    __table_args__ = {'schema': 'MS'}

    id_obj = Column(Integer, primary_key=True)
    id_cob = Column(Integer)
    name_obj = Column(String)
    estandar_code_obj = Column(Integer)
    id_child_obj = Column(Integer)
    description_obj = Column(String)
    orden_obj = Column(Integer)
    owner_data = Column(String)
    estandar_code_cob = Column(String)
    description_cob = Column(String)
    comment_cob = Column(String)


class ServicePoint(Base):
    __tablename__ = 'ms_service_point_spo'
    __table_args__ = {'schema': 'MS'}

    id_spo = Column(Integer, primary_key=True)
    number_spo = Column(String)
    serial_spo = Column(String)
    description_spo = Column(String)
    id_timezone_ste = Column(Integer)
    owner_data = Column(String)


class TransactionResult:
    guid_file = ""
    process = ""
    id_1 = None
    id_2 = None
    message = ""
    result = ""

    def __init__(self, action, entity_1, entity_2=None):
        self.action = action
        self.entity_1 = entity_1
        self.entity_2 = entity_2
        self.datestamp_process = GeneralsUtils.get_datetime()
