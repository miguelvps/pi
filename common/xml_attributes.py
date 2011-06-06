import sqlalchemy

from xser_property import set_xser_prop
import xml_kinds
import xml_types
from xml_kinds import KIND_PROP_NAME as KP
from xml_types import TYPE_PROP_NAME as TP


class AlchemyXserAtribute(object): pass



A= AlchemyXserAtribute
SB= sqlalchemy.types.Boolean
SD= sqlalchemy.types.Date
SS= sqlalchemy.types.String


#PES
class pes_person_birthdate          (SD, A): pass
class pes_person_name               (SS, A): pass
class pes_person_office             (SS, A): pass
class pes_person_email              (SS, A): pass
class pes_person_phone              (SS, A): pass
class pes_person_fax                (SS, A): pass


#DEPARTAMENTOS
##DEPARTMENT
class departamentos_dep_name        (SS, A): pass
class departamentos_dep_acronym     (SS, A): pass 

##COURSE
class departamentos_course_name     (SS, A): pass
class departamentos_course_acronym  (SS, A): pass 
class departamentos_course_type     (SS, A): pass

##SUBJECT
class departamentos_subject_name        (SS, A): pass
class departamentos_subject_acronym     (SS, A): pass
class departamentos_subject_period      (SS, A): pass
class departamentos_subject_regent      (SS, A): pass  
class departamentos_subject_coordinator (SS, A): pass  


#GEO
class geo_placemark_name            (SS, A): pass
class geo_placemark_folder          (SS, A): pass
class geo_placemark_abreviation     (SS, A): pass
class geo_placemark_wkt             (SS, A): pass

class geo_placemarktype_name        (SS, A): pass




# PES atributes properties----------------------------------------------
set_xser_prop(pes_person_birthdate, TP, xml_types.DATETIME_TYPE)
set_xser_prop(pes_person_name, TP, xml_types.STRING_TYPE)
set_xser_prop(pes_person_office, TP, xml_types.STRING_TYPE)
set_xser_prop(pes_person_email, TP, xml_types.EMAIL_TYPE)
set_xser_prop(pes_person_phone, TP, xml_types.STRING_TYPE)
set_xser_prop(pes_person_fax, TP, xml_types.STRING_TYPE)

set_xser_prop(pes_person_name, KP, xml_kinds.person)
set_xser_prop(pes_person_office, KP, xml_kinds.placemark)
set_xser_prop(pes_person_email, KP, xml_kinds.email)
set_xser_prop(pes_person_phone, KP, xml_kinds.phone)
set_xser_prop(pes_person_fax, KP, xml_kinds.fax)

# DEPARTAMENTOS stributes properties -----------------------------------
set_xser_prop(departamentos_dep_name, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_dep_acronym, TP, xml_types.STRING_TYPE)

set_xser_prop(departamentos_course_name, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_course_acronym, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_course_type, TP, xml_types.STRING_TYPE)

set_xser_prop(departamentos_subject_name, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_subject_acronym, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_subject_period, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_subject_regent, TP, xml_types.STRING_TYPE)
set_xser_prop(departamentos_subject_coordinator, TP, xml_types.STRING_TYPE)


set_xser_prop(departamentos_dep_name, KP, xml_kinds.department)
set_xser_prop(departamentos_dep_acronym, KP, xml_kinds.department)

set_xser_prop(departamentos_course_name, KP, xml_kinds.course)
set_xser_prop(departamentos_course_acronym, KP, xml_kinds.course)
set_xser_prop(departamentos_course_type, KP, xml_kinds.course_type)

set_xser_prop(departamentos_subject_name, KP, xml_kinds.subject)
set_xser_prop(departamentos_subject_acronym, KP, xml_kinds.subject)
set_xser_prop(departamentos_subject_period, KP, xml_kinds.subject_period)
set_xser_prop(departamentos_subject_regent, KP, xml_kinds.person)
set_xser_prop(departamentos_subject_coordinator, KP, xml_kinds.person)



#GEO atributes properties----------------------------------------------
set_xser_prop(geo_placemark_name, TP, xml_types.STRING_TYPE)
set_xser_prop(geo_placemark_folder, TP, xml_types.STRING_TYPE)
set_xser_prop(geo_placemark_abreviation, TP, xml_types.STRING_TYPE)
set_xser_prop(geo_placemark_wkt, TP, xml_types.COORDINATE_TYPE)
set_xser_prop(geo_placemarktype_name, TP, xml_types.STRING_TYPE)

set_xser_prop(geo_placemark_name, KP, xml_kinds.placemark)
set_xser_prop(geo_placemark_folder, KP, xml_kinds.placemark_folder)
