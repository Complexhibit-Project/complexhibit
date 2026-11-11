from __future__ import annotations

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator


class CuratedModel(BaseModel):
    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v == "" or v == "-":
                return None
        return v

    @field_validator('nombre', 'name', 'title', check_fields=False)
    @classmethod
    def title_case(cls, v):
        if v and isinstance(v, str):
            return v.title()
        return v


class Imagen(CuratedModel):
    url: Optional[HttpUrl] = None
    name: Optional[str] = None


class Empresa(CuratedModel):
    id: Optional[str] = None
    nombre: str
    categoria_ISIC4: Optional[str] = None
    dimension: Optional[str] = None
    lugar_sede: Optional[str] = None


class Institucion(CuratedModel):
    id: Optional[str] = None
    uri: Optional[str] = None
    nombre: str
    nombre_alternativo: Optional[str] = None
    coordenadas: Optional[str] = None
    correo_electronico: Optional[EmailStr] = None
    direccion_postal: Optional[str] = None
    fax: Optional[str] = None
    lugar_sede: Optional[str] = None
    maximo_responsable: Optional[str] = None
    pagina_web: Optional[str] = None
    telefono: Optional[str] = None
    titularidad: Optional[str] = None
    uri_html: Optional[str] = None
    uri_rss: Optional[str] = None
    palabras_clave: Optional[List[str]] = None
    institucion_matriz: Optional[str] = None
    tipo_institucion: Optional[List[str]] = None


class Persona(CuratedModel):
    id: Optional[str] = None
    uri: Optional[str] = None
    name: str
    gender: Optional[str] = None
    activity: Optional[Union[List[str], str]] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None


class ObraDeArte(CuratedModel):
    class Config:
        arbitrary_types_allowed = True

    id: Optional[str] = None
    uri: Optional[str] = None
    name: str
    apelation: Optional[str] = None
    author: Optional[Dict] = None
    production_start_date: Optional[str] = None
    production_end_date: Optional[str] = None
    production_place: Optional[str] = None
    type: Optional[Union[List[str], str]] = None


class DispositivoDeInscripcion(CuratedModel):
    id: Optional[str] = None
    nombre: str
    lugar_publicacion: Optional[str] = None
    fecha_publicacion: Optional[str] = None
    persona_autora_de_dispositivo_de_inscripcion: Optional[List[str]] = None
    institucion_autora_de_dispositivo_de_inscripcion: Optional[List[str]] = None
    dispositivo_de_inscripcion_patrocinado_por: Optional[List[str]] = None
    ilustrador: Optional[List[str]] = None
    editor: Optional[List[str]] = None
    editorial_del_dispositivo_de_inscripcion: Optional[List[str]] = None
    dispositivo_de_inscripcion_exhibe_persona: Optional[List[str]] = None
    dispositivo_de_inscripcion_exhibe_institucion: Optional[List[str]] = None
    dispositivo_de_inscripcion_exhibe_obra_de_arte: Optional[List[str]] = None
    dispositivo_matriz: Optional[str] = None
    tipo_dispositivo_inscripcion: Optional[List[str]] = None


class Exposicion(CuratedModel):
    id: Optional[str] = None
    uri: Optional[str] = None
    name: str
    fecha_inicio: str
    fecha_fin: str
    direccion_postal: Optional[str] = None
    lugar_celebracion: Optional[str] = None
    coordenadas: Optional[str] = None
    tipo_acceso: Optional[str] = None
    sede: Optional[str] = None
    rango_visitas: Optional[str] = None
    movimiento: Optional[List[str]] = None
    periodo: Optional[List[str]] = None

    comisario: Optional[List[Dict]] = None
    tiene_dispositivo_de_inscripcion: Optional[str] = None
    exposicion_exhibe_artista: Optional[List[Dict]] = None
    exposicion_exhibe_obra_de_arte: Optional[List[Dict]] = None

    fuente_informacion: Optional[List[Dict]] = None
    organiza: Optional[List[Dict]] = None
    institucion_coleccionsita: Optional[List[Dict]] = None
    persona_coleccionsita: Optional[List[Dict]] = None
    exposicion_patrocinada_por: Optional[List[Dict]] = None
    empresa_responsable_museografia: Optional[List[Dict]] = None
    exposicion_matriz: Optional[str] = None
    tipo_exposicion: Optional[List[str]] = None
    website: Optional[str] = None
    catalogue: Optional[str] = None
    flyer: Optional[str] = None
    poster: Optional[str] = None
    review: Optional[str] = None
    pressRelease: Optional[str] = None
    type: Optional[Union[List[str], str]] = None


class Edicion(CuratedModel):
    id: Optional[str] = None
    nombre: str
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    direccion_postal: Optional[str] = None
    lugar_celebracion: Optional[str] = None
    coordenadas: Optional[str] = None
    tipo_acceso: Optional[str] = None
    sede: Optional[str] = None
    rango_visitas: Optional[str] = None
    movimiento: Optional[List[str]] = None
    periodo: Optional[List[str]] = None

    comisario: Optional[List[str]] = None
    tiene_dispositivo_de_inscripcion: Optional[str] = None
    exposicion_exhibe_artista: Optional[List[str]] = None
    exposicion_exhibe_obra_de_arte: Optional[List[str]] = None

    fuente_informacion: Optional[List[str]] = None
    organiza: Optional[List[str]] = None
    institucion_coleccionsita: Optional[List[str]] = None
    persona_coleccionsita: Optional[List[str]] = None
    exposicion_patrocinada_por: Optional[List[str]] = None
    empresa_responsable_museografia: Optional[List[str]] = None
    exposicion_matriz: Optional[str] = None
    tipo_exposicion: Optional[List[str]] = None


Persona.update_forward_refs()
