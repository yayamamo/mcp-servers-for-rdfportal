import requests
import httpx
import json
import sys
from mcp.server.fastmcp import FastMCP
from typing import List, Dict

server = FastMCP("RDF Portal MCP Server")

uniprot_prefixes = '''
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX vg: <http://biohackathon.org/resource/vg#>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX uniprotkb: <http://purl.uniprot.org/uniprot/>
PREFIX uberon: <http://purl.obolibrary.org/obo/uo#>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX SWISSLIPID: <https://swisslipids.org/rdf/SLM_>
PREFIX sp: <http://spinrdf.org/sp#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sd: <http://www.w3.org/ns/sparql-service-description#>
PREFIX schema: <http://schema.org/>
PREFIX sachem: <http://bioinfo.uochb.cas.cz/rdf/v1.0/sachem#>
PREFIX rh: <http://rdf.rhea-db.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX pubmed: <http://rdf.ncbi.nlm.nih.gov/pubmed/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX pr: <http://www.wikidata.org/prop/reference/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX patent: <http://data.epo.org/linked-data/def/patent/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX orthodbGroup: <http://purl.orthodb.org/odbgroup/>
PREFIX orthodb: <http://purl.orthodb.org/>
PREFIX orth: <http://purl.org/net/orth#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX mnx: <https://rdf.metanetx.org/schema/>
PREFIX mnet: <https://rdf.metanetx.org/mnet/>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX lscr: <http://purl.org/lscr#>
PREFIX lipidmaps: <https://www.lipidmaps.org/rdf/>
PREFIX keywords: <http://purl.uniprot.org/keywords/>
PREFIX insdcschema: <http://ddbj.nig.ac.jp/ontologies/nucleotide/>
PREFIX insdc: <http://identifiers.org/insdc/>
PREFIX identifiers: <http://identifiers.org/>
PREFIX GO: <http://purl.obolibrary.org/obo/GO_>
PREFIX glyconnect: <https://purl.org/glyconnect/>
PREFIX glycan: <http://purl.jp/bio/12/glyco/glycan#>
PREFIX genex: <http://purl.org/genex#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX faldo: <http://biohackathon.org/resource/faldo#>
PREFIX eunisSpecies: <http://eunis.eea.europa.eu/rdf/species-schema.rdf#>
PREFIX ensembltranscript: <http://rdf.ebi.ac.uk/resource/ensembl.transcript/>
PREFIX ensemblterms: <http://rdf.ebi.ac.uk/terms/ensembl/>
PREFIX ensemblprotein: <http://rdf.ebi.ac.uk/resource/ensembl.protein/>
PREFIX ensemblexon: <http://rdf.ebi.ac.uk/resource/ensembl.exon/>
PREFIX ensembl: <http://rdf.ebi.ac.uk/resource/ensembl/>
PREFIX ECO: <http://purl.obolibrary.org/obo/ECO_>
PREFIX ec: <http://purl.uniprot.org/enzyme/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX chebislash: <http://purl.obolibrary.org/obo/chebi/>
PREFIX chebihash: <http://purl.obolibrary.org/obo/chebi#>
PREFIX CHEBI: <http://purl.obolibrary.org/obo/CHEBI_>
PREFIX cco: <http://rdf.ebi.ac.uk/terms/chembl#>
PREFIX busco: <http://busco.ezlab.org/schema#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX allie: <http://allie.dbcls.jp/>
'''

sparql_endpoint = {
    "uniprot": "https://rdfportal.org/backend/sib/sparql",
    "pubchem": "https://rdfportal.org/backend/pubchem/sparql"
}

get_proerty_query = '''
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?property
from <http://sparql.uniprot.org/core>
where {
  values ?property_type { owl:ObjectProperty owl:DatatypeProperty }
  values ?property_label { "__QUERY_STR__"^^xsd:string }
  ?property a ?property_type ;
  rdfs:label ?property_label .
}
'''

get_property_list_query = '''
SELECT DISTINCT ?pred WHERE {
  VALUES ?subj { <__URI__> }
  ?subj ?pred ?obj .
}'''

get_class_list_query = '''
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?class
from <http://sparql.uniprot.org/core>
WHERE {
 ?class a owl:Class.
  FILTER (! isBlank(?class) )
}'''

pubchem_prefixes = '''
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX vocab: <http://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary#>
PREFIX ruleset: <http://rdf.ncbi.nlm.nih.gov/pubchem/ruleset/>
PREFIX anatomy: <http://rdf.ncbi.nlm.nih.gov/pubchem/anatomy/>
PREFIX author: <http://rdf.ncbi.nlm.nih.gov/pubchem/author/>
PREFIX bioassay: <http://rdf.ncbi.nlm.nih.gov/pubchem/bioassay/>
PREFIX book: <http://rdf.ncbi.nlm.nih.gov/pubchem/book/>
PREFIX cell: <http://rdf.ncbi.nlm.nih.gov/pubchem/cell/>
PREFIX compound: <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
PREFIX concept: <http://rdf.ncbi.nlm.nih.gov/pubchem/concept/>
PREFIX conserveddomain: <http://rdf.ncbi.nlm.nih.gov/pubchem/conserveddomain/>
PREFIX cooccurrence: <http://rdf.ncbi.nlm.nih.gov/pubchem/cooccurrence/>
PREFIX descriptor: <http://rdf.ncbi.nlm.nih.gov/pubchem/descriptor/>
PREFIX disease: <http://rdf.ncbi.nlm.nih.gov/pubchem/disease/>
PREFIX endpoint: <http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/>
PREFIX gene: <http://rdf.ncbi.nlm.nih.gov/pubchem/gene/>
PREFIX grant: <http://rdf.ncbi.nlm.nih.gov/pubchem/grant/>
PREFIX inchikey: <http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey>
PREFIX journal: <http://rdf.ncbi.nlm.nih.gov/pubchem/journal/>
PREFIX measuregroup: <http://rdf.ncbi.nlm.nih.gov/pubchem/measuregroup/>
PREFIX organization: <http://rdf.ncbi.nlm.nih.gov/pubchem/organization/>
PREFIX patent: <http://rdf.ncbi.nlm.nih.gov/pubchem/patent/>
PREFIX patentassignee: <http://rdf.ncbi.nlm.nih.gov/pubchem/patentassignee/>
PREFIX patentinventor: <http://rdf.ncbi.nlm.nih.gov/pubchem/patentinventor/>
PREFIX patentcpc: <http://rdf.ncbi.nlm.nih.gov/pubchem/patentcpc/>
PREFIX patentipc: <http://rdf.ncbi.nlm.nih.gov/pubchem/patentipc/>
PREFIX pathway: <http://rdf.ncbi.nlm.nih.gov/pubchem/pathway/>
PREFIX protein: <http://rdf.ncbi.nlm.nih.gov/pubchem/protein/>
PREFIX reaction: <http://rdf.ncbi.nlm.nih.gov/pubchem/reaction/>
PREFIX reference: <http://rdf.ncbi.nlm.nih.gov/pubchem/reference/>
PREFIX source: <http://rdf.ncbi.nlm.nih.gov/pubchem/source/>
PREFIX substance: <http://rdf.ncbi.nlm.nih.gov/pubchem/substance/>
PREFIX synonym: <http://rdf.ncbi.nlm.nih.gov/pubchem/synonym/>
PREFIX taxonomy: <http://rdf.ncbi.nlm.nih.gov/pubchem/taxonomy/>
PREFIX bao: <http://www.bioassayontology.org/bao#>
PREFIX bp3: <http://www.biopax.org/release/biopax-level3.owl#>
PREFIX chembl: <http://rdf.ebi.ac.uk/resource/chembl/molecule/>
PREFIX chembl.assay: <http://rdf.ebi.ac.uk/resource/chembl/assay/>
PREFIX cheminf: <http://semanticscience.org/resource/>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX edam: <http://edamontology.org/>
PREFIX efo: <http://www.ebi.ac.uk/efo/>
PREFIX ensembl: <http://rdf.ebi.ac.uk/resource/ensembl/>
PREFIX epo_cpc: <http://data.epo.org/linked-data/def/cpc/>
PREFIX epo_ipc: <http://data.epo.org/linked-data/def/ipc/>
PREFIX epo_patent: <http://data.epo.org/linked-data/def/patent/>
PREFIX fabio: <http://purl.org/spar/fabio/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX frapo: <http://purl.org/cerif/frapo/>
PREFIX idorg: <http://identifiers.org/>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
PREFIX ndfrt: <http://purl.bioontology.org/ontology/NDFRT>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX pav: <http://purl.org/pav/>
PREFIX pdbo: <http://rdf.wwpdb.org/schema/pdbx-v50.owl#>
PREFIX prism: <http://prismstandard.org/namespaces/basic/3.0/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX snomedct: <http://purl.bioontology.org/ontology/SNOMEDCT>
PREFIX uniprot: <http://purl.uniprot.org/uniprot/>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX vcard2006: <http://www.w3.org/2006/vcard/ns#>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX wd: <http://www.wikidata.org/entity/>
'''

sparql_endpoint = {
    "uniprot": "https://rdfportal.org/backend/sib/sparql",
    "pubchem": "https://rdfportal.org/backend/pubchem/sparql"
}

get_proerty_query = '''
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?property
from <http://sparql.uniprot.org/core>
where {
  values ?property_type { owl:ObjectProperty owl:DatatypeProperty }
  values ?property_label { "__QUERY_STR__"^^xsd:string }
  ?property a ?property_type ;
  rdfs:label ?property_label .
}
'''

get_property_list_query = '''
SELECT DISTINCT ?pred WHERE {
  VALUES ?subj { <__URI__> }
  ?subj ?pred ?obj .
}'''

get_class_list_query = '''
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?class
from <http://sparql.uniprot.org/core>
WHERE {
 ?class a owl:Class.
  FILTER (! isBlank(?class) )
}'''

def issue_sparql_query(sparql_query: str, endpoint: str) -> str:
    data = []
    resp = httpx.post(
        sparql_endpoint[endpoint],
        data = {"query": sparql_query},
        headers={"Accept": "application/sparql-results+json",
                 "Content-Type": "application/x-www-form-urlencoded"}
    )
    if resp.status_code == 200 and "json" in resp.headers.get("Content-Type", ""):
        data = resp.json()
        return [entry["pred"]["value"] for entry in data["results"]["bindings"]]
    else:
        print("Bad response:\n", resp.text, file=sys.stderr)
        return data

@server.tool()
async def execute_sparql_for_pubchem(sparql_query: str) -> str:
    """
    Execute a SPARQL query on RDF Portal PubChem endpoint.

    Args:
        sparql_query (str): The SPARQL query to execute.
        Note that any compound name needs to be expressed a PubChem compound ID URI such as http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID60823
        In addition, there are following named graphs.
            http://rdf.ncbi.nlm.nih.gov/pubchem/anatomy
            http://rdf.ncbi.nlm.nih.gov/pubchem/author
            http://rdf.ncbi.nlm.nih.gov/pubchem/bioassay
            http://rdf.ncbi.nlm.nih.gov/pubchem/book
            http://rdf.ncbi.nlm.nih.gov/pubchem/cell
            http://rdf.ncbi.nlm.nih.gov/pubchem/compound
            http://rdf.ncbi.nlm.nih.gov/pubchem/concept
            http://rdf.ncbi.nlm.nih.gov/pubchem/conserveddomain
            http://rdf.ncbi.nlm.nih.gov/pubchem/cooccurrence
            http://rdf.ncbi.nlm.nih.gov/pubchem/descriptor/compound
            http://rdf.ncbi.nlm.nih.gov/pubchem/descriptor/substance
            http://rdf.ncbi.nlm.nih.gov/pubchem/disease
            http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint
            http://rdf.ncbi.nlm.nih.gov/pubchem/gene
            http://rdf.ncbi.nlm.nih.gov/pubchem/grant
            http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey
            http://rdf.ncbi.nlm.nih.gov/pubchem/journal
            http://rdf.ncbi.nlm.nih.gov/pubchem/measuregroup
            http://rdf.ncbi.nlm.nih.gov/pubchem/organization
            http://rdf.ncbi.nlm.nih.gov/pubchem/patent
            http://rdf.ncbi.nlm.nih.gov/pubchem/pathway
            http://rdf.ncbi.nlm.nih.gov/pubchem/protein
            http://rdf.ncbi.nlm.nih.gov/pubchem/reference
            http://rdf.ncbi.nlm.nih.gov/pubchem/source
            http://rdf.ncbi.nlm.nih.gov/pubchem/substance
            http://rdf.ncbi.nlm.nih.gov/pubchem/synonym
            http://rdf.ncbi.nlm.nih.gov/pubchem/taxonomy
        Furthermore, when obtaining a protein data with UniProt ID, its prefix should be changed from http://purl.uniprot.org/uniprot/ to http://rdf.ncbi.nlm.nih.gov/pubchem/protein/ACC such as http://rdf.ncbi.nlm.nih.gov/pubchem/protein/ACCQ9Y6E7 for the UniProt ID of Q9Y6E7.
        Do not use the back-slash symbol to escape a double-quotation. There is no need to escape quotation and double-quotation marks.
        You can use a shape expression of PubChem RDF by obtaining shex://shape-expression/pubchem.shexj

    Returns:
        str: The JSON-formatted result of the SPARQL query execution. If there are no results, an empty JSON object will be returned.
    """
    sparql_query = pubchem_prefixes + sparql_query
    async with httpx.AsyncClient() as client:
        response = await client.get(
            sparql_endpoint["pubchem"], params={"query": sparql_query, "format": "json"}
        )
    response.raise_for_status()
    result = response.json()["results"]["bindings"]
    return json.dumps(result)

@server.tool()
def get_pubchem_compound_id(compound_name: str):
    """
    Get a PubChem compound ID

    Args: Compound name
        example: "resveratrol"

    Returns: PubChem Compound ID in the JSON format
    """
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"

    response = requests.get(url)
    return response.json()

@server.tool()
def get_compound_attributes_from_pubchem(pubchem_compound_id: str):
    """
    Get compound attributes from PubChem RDF

    Args: PubChem Compound ID
        example: "445154"

    Returns: Compound attributes in the JSON format
    """
    url = "https://togodx.dbcls.jp/human/sparqlist/api/metastanza_pubchem_compound"

    params = {
        "id": pubchem_compound_id,
    }
    response = requests.get(url, params=params)
    return response.json()

@server.prompt(name="Query by SPARQL")
def build_sparql_query() -> str:
    return "When building a SPARQL query, please refer a relevant shape expressions provided with the resource."

@server.resource("shex://shape-expression/pubchem.shexj")
def get_shex() -> str:
    """Show a shape expression for PubChem RDF in JSON, which can be used to build a SPARQL query"""
    with open("/Users/yayamamo/git/mcp-pubchem/pubchem.shexj", "r") as file:
        shex = file.read()
    return shex

async def get_protein_id(query: str) -> str:
    url = "https://rest.uniprot.org/uniprotkb/search"

    params = {
        "query": query,
        "fields": "accession,protein_name,gene_names,organism_name",
        "format": "json",
        "size": 50  # optional, limit results
    }
    response = requests.get(url, params=params)
    data = response.json()

    uniprot_id_list = []
    for entry in data.get("results", []):
        try:
            #name = entry["proteinDescription"]["recommendedName"]["fullName"]["value"]
            #if name.lower().startswith("insulin"):
            #if query in name:
                uniprot_id = entry["primaryAccession"]
                uniprot_id_list.append(uniprot_id)
                #print(f"{uniprot_id}: {name}")
        except KeyError:
            continue  # skip entries without expected structure

    return json.dumps(uniprot_id_list)

@server.tool()
async def search_uniprot_entity(query: str) -> str:
    """
    Search for a UniProt entity ID by its query.

    Args:
        query (str): The query to search for. The query should be unambiguous enough to uniquely identify the entity.

    Returns:
        str: The UniProt protein entity ID corresponding to the given query."
    """
    return await get_protein_id(query)


@server.tool()
async def search_uniprot_property(query: str) -> str:
    """
    Search for a UniProt property URI by its query.

    Args:
        query (str): The query to search for. The query should be unambiguous enough to uniquely identify the property.

    Returns:
        URI: The UniProt property URI corresponding to the given query."
    """
    return issue_sparql_query(get_proerty_query.replace('__QUERY_STR__', query), "uniprot")

@server.resource("rdf://classes/list.json")
async def search_class_list() -> str:
    return issue_sparql_query(get_class_list_query, "uniprot")

@server.tool()
async def get_uniprot_properties(entity_uri: str) -> List[str]:
    """
    Get the properties associated with a given URI.

    Args:
        entity_id (str): The UniProt URI to retrieve properties for. This should be a valid UniProt entity URI.
        Notably, UniProt an entity URI starts with "http://purl.uniprot.org/uniprot/".

    Returns:
        list: A list of property URIs associated with the given URI. If no properties are found, an empty list is returned.
    """
    return issue_sparql_query(get_property_list_query.replace('__QUERY_STR__', entity_uri), "uniprot")

@server.tool()
async def execute_sparql_uniprot(sparql_query: str) -> str:
    """
    Execute a SPARQL query on RDF Portal.
    You can use a shape expression of UniProt RDF by obtaining shex://shape-expression/uniprot.shexj

    Args:
        sparql_query (str): The SPARQL query to execute.

    Returns:
        str: The JSON-formatted result of the SPARQL query execution. If there are no results, an empty JSON object will be returned.
    """
    sparql_query = uniprot_prefixes + sparql_query
    async with httpx.AsyncClient() as client:
        response = await client.get(
            sparql_endpoint["uniprot"], params={"query": sparql_query, "format": "json"}
        )
    response.raise_for_status()
    result = response.json()["results"]["bindings"]
    return json.dumps(result)

@server.resource("shex://shape-expression/uniprot.shexj")
def get_shex() -> str:
    """Show a shape expression for UniProt RDF in JSON, which can be used to build a SPARQL query"""
    with open("/Users/yayamamo/git/mcp-sparql/uniprot.shexj", "r") as file:
        shex = file.read()
    return shex

if __name__ == "__main__":
    server.run()