import requests
import pandas as pd
import os

def buscar_clinicas(cidade):
    print(f"Buscando clínicas em {cidade}...")
    
    # Endpoint público da Overpass API
    url = "http://overpass-api.de/api/interpreter"

    # Query na linguagem do Overpass para buscar clínicas e médicos na cidade alvo
    query = f"""
    [out:json];
    area[name="{cidade}"]->.searchArea;
    (
      node["amenity"="clinic"](area.searchArea);
      node["amenity"="doctors"](area.searchArea);
      node["healthcare"="clinic"](area.searchArea);
    );
    out tags;
    """

    # Fazendo a requisição
    resposta = requests.get(url, params={'data': query})
    data = resposta.json()

    clinicas = []
    
    # Processando o JSON retornado
    for elemento in data.get('elements', []):
        tags = elemento.get('tags', {})

        # Filtra apenas locais que tenham o nome registrado
        if 'name' in tags:
            clinica = {
                'Nome': tags.get('name', 'N/A'),
                'Telefone': tags.get('phone', tags.get('contact:phone', 'N/A')),
                'Site': tags.get('website', tags.get('contact:website', 'N/A')),
                # Monta o endereço concatenando rua e número, se existirem
                'Endereço': f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(),
                'Cidade': cidade
            }
            clinicas.append(clinica)

    return clinicas

def principal():
    # Nossos alvos iniciais
    cidades_alvo = ["Curitiba", "Paranaguá"]
    todas_clinicas = []

    # Itera sobre as cidades e junta os resultados
    for cidade in cidades_alvo:
        resultados = buscar_clinicas(cidade)
        todas_clinicas.extend(resultados)

    # Cria a pasta 'data' caso ela ainda não exista
    os.makedirs('data', exist_ok=True)

    # Converte a lista de dicionários em um DataFrame do pandas
    df = pd.DataFrame(todas_clinicas)

    # Limpeza básica: substitui endereços vazios por 'N/A'
    df['Endereço'] = df['Endereço'].replace('', 'N/A')

    # Exportando os dados
    df.to_csv('data/clinicas.csv', index=False, encoding='utf-8')
    df.to_json('data/clinicas.json', orient='records', force_ascii=False, indent=4)

    print(f"\nExtração concluída com sucesso! {len(todas_clinicas)} contatos encontrados.")
    print("Arquivos salvos na pasta 'data/'.")

if __name__ == "__main__":
    principal()