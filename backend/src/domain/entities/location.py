"""
Location Value Object

Value Object representando uma localização geográfica.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """
    Value Object para localização geográfica.

    Imutável e usado para representar coordenadas de instrutores.
    Utiliza o sistema de referência WGS 84 (SRID 4326).

    Attributes:
        latitude: Latitude em graus decimais (-90 a 90).
        longitude: Longitude em graus decimais (-180 a 180).
    """

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Valida as coordenadas após inicialização."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude inválida: {self.latitude}. Deve estar entre -90 e 90.")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude inválida: {self.longitude}. Deve estar entre -180 e 180.")

    def to_wkt(self) -> str:
        """
        Converte para formato WKT (Well-Known Text) para PostGIS.

        Returns:
            String no formato 'POINT(longitude latitude)'.
        """
        return f"POINT({self.longitude} {self.latitude})"

    @classmethod
    def from_wkt(cls, wkt: str) -> "Location":
        """
        Cria Location a partir de string WKT.

        Args:
            wkt: String no formato 'POINT(longitude latitude)'.

        Returns:
            Instância de Location.

        Raises:
            ValueError: Se o formato WKT for inválido.
        """
        try:
            # Remove 'POINT(' e ')' e separa coordenadas
            coords = wkt.replace("POINT(", "").replace(")", "").strip().split()
            longitude = float(coords[0])
            latitude = float(coords[1])
            return cls(latitude=latitude, longitude=longitude)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Formato WKT inválido: {wkt}") from e

    def distance_to(self, other: "Location") -> float:
        """
        Calcula distância aproximada em km usando fórmula de Haversine.

        Nota: Para cálculos precisos, use PostGIS ST_Distance.

        Args:
            other: Outra localização para calcular distância.

        Returns:
            Distância em quilômetros.
        """
        import math

        R = 6371  # Raio da Terra em km

        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        delta_lat = math.radians(other.latitude - self.latitude)
        delta_lon = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
