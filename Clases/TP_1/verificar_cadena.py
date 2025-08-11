import json
import hashlib
import sys
import os

class BlockchainVerifier:
    """Verificador de integridad de la cadena de bloques"""
    
    def __init__(self, blockchain_file="blockchain.json"):
        self.blockchain_file = blockchain_file
        self.blockchain = []
        
    def load_blockchain(self):
        """Carga la cadena de bloques desde el archivo"""
        try:
            # Si la ruta no es absoluta, buscar en el directorio del script
            if not os.path.isabs(self.blockchain_file):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(script_dir, self.blockchain_file)
            else:
                full_path = self.blockchain_file
                
            with open(full_path, 'r') as f:
                self.blockchain = json.load(f)
            print(f"Cadena de bloques cargada desde: {full_path}")
            print(f"Total de bloques: {len(self.blockchain)}")
            return True
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.blockchain_file}")
            if not os.path.isabs(self.blockchain_file):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(script_dir, self.blockchain_file)
                print(f"Buscado en: {full_path}")
            return False
        except json.JSONDecodeError:
            print(f"Error: El archivo {self.blockchain_file} no es un JSON válido")
            return False
        except Exception as e:
            print(f"Error al cargar blockchain: {e}")
            return False
    
    def calculate_hash(self, block_data, prev_hash, timestamp):
        """Calcula el hash SHA-256 del bloque"""
        content = prev_hash + str(block_data) + timestamp
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_block_hash(self, block):
        """Verifica el hash de un bloque individual"""
        calculated_hash = self.calculate_hash(
            block["datos"], 
            block["prev_hash"], 
            block["timestamp"]
        )
        return calculated_hash == block["hash"]
    
    def verify_chain_integrity(self):
        """Verifica la integridad completa de la cadena"""
        if not self.blockchain:
            print("Error: La cadena de bloques está vacía")
            return False
        
        corrupted_blocks = []
        chain_valid = True
        
        print("Verificando integridad de la cadena de bloques...")
        
        for i, block in enumerate(self.blockchain):
            # Verificar hash del bloque
            if not self.verify_block_hash(block):
                corrupted_blocks.append(i)
                chain_valid = False
                print(f"CORRUPTO: Bloque {i} - Hash inválido")
            
            # Verificar encadenamiento (excepto el primer bloque)
            if i > 0:
                prev_block = self.blockchain[i-1]
                if block["prev_hash"] != prev_block["hash"]:
                    corrupted_blocks.append(i)
                    chain_valid = False
                    print(f"CORRUPTO: Bloque {i} - Hash previo no coincide")
            else:
                # Primer bloque debe tener prev_hash = "0"
                if block["prev_hash"] != "0":
                    corrupted_blocks.append(i)
                    chain_valid = False
                    print(f"CORRUPTO: Bloque {i} - Hash previo del primer bloque debe ser '0'")
        
        if chain_valid:
            print("La cadena de bloques es íntegra - No hay bloques corruptos")
        else:
            print(f"Se encontraron {len(corrupted_blocks)} bloques corruptos")
            print(f"Bloques corruptos: {corrupted_blocks}")
        
        return chain_valid, corrupted_blocks
    
    def generate_report(self, integrity_result):
        """Genera un reporte de la cadena de bloques"""
        if not self.blockchain:
            print("Error: No hay datos para generar el reporte")
            return
        
        total_blocks = len(self.blockchain)
        alert_blocks = sum(1 for block in self.blockchain if block["alerta"])
        
        # Calcular promedios generales
        freq_sum = press_sum = oxygen_sum = 0
        
        for block in self.blockchain:
            freq_sum += block["datos"]["frecuencia"]["media"]
            press_sum += block["datos"]["presion"]["media"]
            oxygen_sum += block["datos"]["oxigeno"]["media"]
        
        avg_frequency = freq_sum / total_blocks
        avg_pressure = press_sum / total_blocks
        avg_oxygen = oxygen_sum / total_blocks
        
        # Crear reporte
        report_content = f"""=== REPORTE DE ANÁLISIS BIOMÉTRICO ===

Información General:
- Total de bloques: {total_blocks}
- Bloques con alertas: {alert_blocks}
- Porcentaje de alertas: {(alert_blocks/total_blocks)*100:.1f}%

Promedios Generales:
- Frecuencia cardíaca promedio: {avg_frequency:.2f} bpm
- Presión arterial promedio: {avg_pressure:.2f} mmHg
- Oxígeno en sangre promedio: {avg_oxygen:.2f}%

Análisis de Alertas:
"""
        
        if alert_blocks > 0:
            report_content += f"Se detectaron {alert_blocks} bloques con valores fuera del rango normal.\n"
            report_content += "Timestamps con alertas:\n"
            
            for i, block in enumerate(self.blockchain):
                if block["alerta"]:
                    report_content += f"  - Bloque {i+1}: {block['timestamp']}\n"
        else:
            report_content += "No se detectaron alertas en ningún bloque.\n"
        
        report_content += f"""
Verificación de Integridad:
"""
        
        # Usar el resultado de integridad (que siempre debe estar presente)
        is_valid, corrupted = integrity_result
        if is_valid:
            report_content += "La cadena de bloques mantiene su integridad.\n"
        else:
            report_content += f"Se encontraron {len(corrupted)} bloques corruptos.\n"
        
        report_content += f"""
Fecha del reporte: {self.blockchain[0]['timestamp']} - {self.blockchain[-1]['timestamp']}
"""
        
        # Guardar reporte en la misma carpeta que el script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        report_path = os.path.join(script_dir, "reporte.txt")
        
        with open(report_path, "w") as f:
            f.write(report_content)
        
        print(f"Reporte generado en '{report_path}'")
        print("\n" + report_content)


def main():
    """Función principal"""
    print("=== Verificador de Integridad de Cadena de Bloques ===")
    
    # Verificar argumentos
    blockchain_file = "blockchain.json"
    if len(sys.argv) > 1:
        blockchain_file = sys.argv[1]
    
    # Crear verificador
    verifier = BlockchainVerifier(blockchain_file)
    
    # Cargar cadena de bloques
    if not verifier.load_blockchain():
        sys.exit(1)
    
    # Verificar integridad (solo una vez)
    integrity_result = verifier.verify_chain_integrity()
    
    # Generar reporte pasando el resultado de la verificación
    verifier.generate_report(integrity_result)


if __name__ == "__main__":
    main()
