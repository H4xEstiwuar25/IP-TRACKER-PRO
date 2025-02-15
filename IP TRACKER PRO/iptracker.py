import asyncio
import httpx
import folium
import sys
import os
from rich.console import Console
from rich.table import Table

# Configuración de colores y consola
console = Console()

# Banner llamativo
BANNER = """\033[31m
████████╗██████╗ ███████╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
   ██║   ██████╔╝█████╗  ███████║██║     █████╔╝ █████╗  ██████╔╝
   ██║   ██╔═══╝ ██╔══╝  ██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
   ██║   ██║     ███████╗██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  
   \033[36mIP TRACKER PRO - Localización y detalles de direcciones IP\033[0m
   \033[33mCoded by: H4xEstiwuar 🚀\033[0m
"""

# URL de la API
API_URL = "http://ip-api.com/json/"

async def consultar_ip(client, ip):
    """Consulta la API de ip-api.com para obtener datos de una IP."""
    try:
        response = await client.get(API_URL + ip)
        data = response.json()

        if data["status"] == "fail":
            return {"IP": ip, "Error": "IP inválida o bloqueada"}

        return {
            "IP": data["query"],
            "ISP": data["isp"],
            "Org": data.get("org", "N/A"),
            "Ciudad": data["city"],
            "Región": data["regionName"],
            "Latitud": data["lat"],
            "Longitud": data["lon"],
            "Zona Horaria": data["timezone"],
            "Código Postal": data["zip"],
        }
    except httpx.RequestError:
        return {"IP": ip, "Error": "No se pudo conectar a la API"}

def crear_mapa(lat, lon, saveMap):
    """Crear un mapa con folium mostrando la ubicación de la IP."""
    # Obtener la ruta absoluta del directorio actual (el proyecto)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    map_dir = os.path.join(base_dir, "Mapas")

    # Asegurar que la carpeta "Mapas" existe dentro del proyecto
    if not os.path.exists(map_dir):
        os.makedirs(map_dir)

    # Guardar el mapa en la carpeta "Mapas"
    map_path = os.path.join(map_dir, f"{saveMap}.html")

    map = folium.Map(location=[lat, lon], zoom_start=12)
    folium.CircleMarker(location=[lat, lon], radius=50, popup="Localización IP", color="red").add_to(map)
    map.save(map_path)

    console.print(f"[bold green]Mapa guardado en {map_path}[/bold green]")

async def main():
    """Función principal del script."""
    print(BANNER)  # Muestra el banner

    # Solicitar la IP al usuario
    ip = input("Ingrese la IP a buscar: ").strip()

    if not ip:
        console.print("[bold red]Error:[/bold red] Debes ingresar una IP válida.")
        sys.exit(1)

    # Consultar la IP de manera asíncrona
    async with httpx.AsyncClient() as client:
        resultado = await consultar_ip(client, ip)

    # Mostrar resultado en una tabla
    table = Table(title="Información de la IP", header_style="bold cyan")
    table.add_column("IP", style="bold yellow")
    table.add_column("ISP")
    table.add_column("Org")
    table.add_column("Ciudad")
    table.add_column("Región")
    table.add_column("Latitud", justify="right")
    table.add_column("Longitud", justify="right")
    table.add_column("Zona Horaria")
    table.add_column("Código Postal")

    if "Error" in resultado:
        console.print(f"[bold red]{resultado['IP']} - {resultado['Error']}[/bold red]")
    else:
        table.add_row(
            resultado["IP"], resultado["ISP"], resultado["Org"], resultado["Ciudad"],
            resultado["Región"], str(resultado["Latitud"]), str(resultado["Longitud"]),
            resultado["Zona Horaria"], resultado["Código Postal"]
        )
        console.print(table)

        # Crear y guardar el mapa con folium en la carpeta "Mapas"
        saveMap = input("Ingrese el nombre del mapa: ")
        crear_mapa(resultado["Latitud"], resultado["Longitud"], saveMap)

# Ejecutar script
if __name__ == "__main__":
    asyncio.run(main())



