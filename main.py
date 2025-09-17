import sys
import requests
import httpx
import xml.etree.ElementTree as ET
from fastmcp import FastMCP
#from mcp.server.fastmcp import FastMCP

server = FastMCP("RDF Portal MCP Server")

# ======== 既存の get_synonym_URIs を利用 =========
sparql_endpoint = {
    "uniprot": "https://rdfportal.org/backend/sib/sparql",
    "pubchem": "https://rdfportal.org/backend/pubchem/sparql",
    "primary": "https://rdfportal.org/backend/primary/sparql",
    "fedx":    "https://plod.dbcls.jp/repositories/RDF_Portal"
}

equivalent_prefix_pairs = [
      ['http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey/', 'http://identifiers.org/inchikey/'],
      ['http://identifiers.org/inchikey/', 'http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey/'],
      ['http://rdf.ncbi.nlm.nih.gov/pubchem/compound/', 'http://identifiers.org/pubchem.compound/'],
      ['http://rdf.ncbi.nlm.nih.gov/pubchem/gene/GID', 'http://identifiers.org/ncbigene/'],
      ['http://bio2rdf.org/geneid:', 'http://identifiers.org/ncbigene/'],
      ['http://glycosmos.org/glycogene/', 'http://identifiers.org/ncbigene/'],
      ['http://identifiers.org/ctd.gene/', 'http://identifiers.org/ncbigene/'],
      ['http://purl.uniprot.org/geneid/', 'http://identifiers.org/ncbigene/'],
      ['http://linkedlifedata.com/resource/entrezgene/id/', 'http://identifiers.org/ncbigene/'],
      ['http://identifiers.org/genewiki/', 'http://identifiers.org/ncbigene/'],
      ['http://rdf.ncbi.nlm.nih.gov/pubchem/protein/ACC', 'http://identifiers.org/uniprot/'],
      ['http://purl.uniprot.org/uniprot/', 'http://rdf.ncbi.nlm.nih.gov/pubchem/protein/ACC'],
      ['http://purl.uniprot.org/uniprot/', 'http://identifiers.org/uniprot/'],
      ['http://identifiers.org/ncbiprotein:', 'http://identifiers.org/uniprot/'],
      ['http://identifiers.org/uniprot:', 'http://identifiers.org/uniprot/'],
      ['http://rdf.ncbi.nlm.nih.gov/pubchem/protein/EC_', 'http://identifiers.org/ec-code/'],
      ['http://purl.uniprot.org/enzyme/', 'http://identifiers.org/ec-code/'],
      ['http://rdf.ncbi.nlm.nih.gov/pubchem/taxonomy/TAXID', 'http://identifiers.org/taxonomy/'],
      ['http://purl.obolibrary.org/obo/NCBITaxon_', 'http://identifiers.org/taxonomy/'],
      ['http://ddbj.nig.ac.jp/ontologies/taxonomy/', 'http://identifiers.org/taxonomy/'],
      ['http://purl.org/obo/owl/NCBITaxon#', 'http://identifiers.org/taxonomy/'],
      ['http://www.berkeleybop.org/ontologies/owl/NCBITaxon#', 'http://identifiers.org/taxonomy/'],
      ['http://purl.uniprot.org/taxonomy/', 'http://identifiers.org/taxonomy/'],
      ['http://purl.uniprot.org/intact/', 'http://identifiers.org/intact/'],
      ['https://www.ebi.ac.uk/intact/search?query=', 'http://identifiers.org/intact/'],
      ['http://purl.obolibrary.org/obo/CHEBI_', 'http://identifiers.org/CHEBI:'],
      ['http://purl.obolibrary.org/obo/DOID_', 'http://identifiers.org/DOID:'],
      ['http://bioportal.bioontology.org/ontologies/DOID/DOID:', 'http://identifiers.org/DOID:'],
      ['http://glycosmos.org/disease/DOID:', 'http://identifiers.org/DOID:'],
      ['http://purl.obolibrary.org/obo/GO_', 'http://identifiers.org/GO:'],
      ['http://identifiers.org/obo.go/GO:', 'http://identifiers.org/GO:'],
      ['http://purl.obolibrary.org/obo/HP_', 'http://identifiers.org/HP:'],
      ['http://linkedlifedata.com/resource/phenotype/id/HP:', 'http://identifiers.org/HP:'],
      ['http://purl.obolibrary.org/obo/MONDO_', 'https://identifiers.org/mondo:'],
      ['http://purl.obolibrary.org/obo/NCIT_', 'http://identifiers.org/ncit:'],
      ['http://purl.obolibrary.org/obo/UBERON_', 'http://identifiers.org/UBERON:'],
      ['http://uri.neuinfo.org/nif/nifstd/UBERON_', 'http://identifiers.org/UBERON:'],
      ['http://rdf.ebi.ac.uk/resource/ensembl/', 'http://identifiers.org/ensembl/'],
      ['http://icgc.link/Gene/', 'http://identifiers.org/ensembl/'],
      ['http://identifiers.org/fb/', 'http://identifiers.org/ensembl/'],
      ['http://identifiers.org/wb/', 'http://identifiers.org/ensembl/'],
      ['http://rdf.ebi.ac.uk/resource/chembl/molecule/', 'http://identifiers.org/chembl.compound/'],
      ['http://rdf.ebi.ac.uk/resource/ensembl/LRG_', 'http://identifiers.org/lrg/LRG_'],
      ['https://www.ebi.ac.uk/interpro/protein/reviewed/', 'http://identifiers.org/interpro/'],
      ['http://rdf.ncbi.nlm.nih.gov/pubmed/', 'http://identifiers.org/pubmed/'],
      ['http://linkedlifedata.com/resource/pubmed/id/', 'http://identifiers.org/pubmed/'],
      ['http://identifiers.org/pubmed:', 'http://identifiers.org/pubmed/'],
      ['http://id.nlm.nih.gov/mesh/', 'http://identifiers.org/mesh/'],
      ['http://purl.jp/bio/101/opentggates/Probe/', 'http://identifiers.org/affy.probeset/'],
      ['http://www.ensembl.org/Homo_sapiens/Variation/Explore?v=', 'http://identifiers.org/dbsnp/'],
      ['http://bio2rdf.org/dbsnp:', 'http://identifiers.org/dbsnp/'],
      ['http://www.ncbi.nlm.nih.gov/SNP/snp_ref.cgi?rs=', 'http://identifiers.org/dbsnp/'],
      ['http://www.snpedia.com/index.php/', 'http://identifiers.org/dbsnp/'],
      ['http://www.ncbi.nlm.nih.gov/clinvar/?term=', 'http://identifiers.org/dbsnp/'],
      ['https://www.bgee.org/bgee15_1/gene/', 'http://identifiers.org/oma.grp/'],
      ['http://omabrowser.org/ontology/oma#GENE_', 'http://identifiers.org/oma.grp/'],
      ['http://rdf.glycoinfo.org/glycan/', 'http://identifiers.org/glytoucan/'],
      ['http://www.glytoucan.org/Structures/Glycans/', 'http://identifiers.org/glytoucan/'],
      ['http://glytoucan.org/Structures/Glycans/', 'http://identifiers.org/glytoucan/'],
      ['http://purl.obolibrary.org/obo/GNO_', 'http://identifiers.org/glytoucan/'],
]

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        # xが初めて出てきたら、自分自身を親に設定
        if x not in self.parent:
            self.parent[x] = x
        # 経路圧縮
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        # find() を呼ぶ前に初期化されていることを保証
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_a] = root_b


# 同義グループ構築
uf = UnionFind()
for a, b in equivalent_prefix_pairs:
    uf.union(a, b)

# グループ辞書
from collections import defaultdict
groups = defaultdict(set)
for prefix in uf.parent:
    groups[uf.find(prefix)].add(prefix)

prefix_to_group = {}
for group in groups.values():
    for p in group:
        prefix_to_group[p] = group

# --- 2. マッチするprefixを探して置換 ---
# URI変換関数
def _get_equivalent_uris(uri):
    for prefix in prefix_to_group:
        if uri.startswith(prefix):
            suffix = uri[len(prefix):]
            return [p + suffix for p in prefix_to_group[prefix]]
    return [uri]

from typing import List

def issue_sparql_query_for_togoid(source_uri: str) -> List[str]:
    """
    Issue a SPARQL query to the RDF Portal primary endpoint to get TogoID relations.

    Args:
        source_uri (str): The URI to get equivalent URIs for.

    Returns:
        List[str]: A list of URIs from the results of the SPARQL query.
    """
    sparql_query = f'''SELECT distinct ?uri
    WHERE {{ <{source_uri}> (<http://togoid.dbcls.jp/ontology#TIO_000001>|<http://togoid.dbcls.jp/ontology#TIO_000002>) ?uri }}'''

    '''
        async with httpx.AsyncClient() as client:
        response = await client.get(
            sparql_endpoint["pubchem"], params={"query": sparql_query, "format": "json"}
        )
    response.raise_for_status()
    '''

    data = []
    resp = httpx.post(
        sparql_endpoint["primary"],
        data={"query": sparql_query},
        headers={"Accept": "application/sparql-results+json",
                 "Content-Type": "application/x-www-form-urlencoded"}
    )
    if resp.status_code == 200 and "json" in resp.headers.get("Content-Type", ""):
        data = resp.json()
        return [entry["uri"]["value"] for entry in data["results"]["bindings"]]
    else:
        print("Bad response:\n", resp.text, file=sys.stderr)
        return data

def get_synonym_URIs(src_uri: str) -> List[str]:
    """
    Get equivalent or synonym URIs for a given URI.

    Args:
        src_uri (str): The URI to get synonyms for.

    Returns:
        List[str]: A list of synonym URIs.
    """
    if not src_uri.startswith("http"):
        raise ValueError("The URI must start with 'http' or 'https'.")

    equivalent_uris = set()
    for uri in _get_equivalent_uris(src_uri):
        equivalent_uris.add(uri)
        for togoid_uri in issue_sparql_query_for_togoid(uri):
            equivalent_uris.add(togoid_uri)
            for equivalent_uri in _get_equivalent_uris(togoid_uri):
                equivalent_uris.add(equivalent_uri)
    #print('\n'.join(equivalent_uris))
    return list(equivalent_uris)

#def get_synonym_URIs(uri: str) -> List[str]:
    # ここでは既存の実装を呼ぶ前提
    # (prefixの違いは UnionFind + equivalent_prefix_pairs,
    #  命名規則の違いは TogoID を利用)
    # 本物の実装をそのまま差し込んでください
#    return [uri]  # ← ダミー。実際は synonyms を返す


# ======== アダプター層 =========

# --- PubMed ---
async def pubmed_search(query: str):
    entrez_endpoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            entrez_endpoint + "/esearch.fcgi",
            params={"db": "pubmed", "term": query, "usehistory": "n"}
        )
    response.raise_for_status()
    tree = ET.ElementTree(ET.fromstring(response.text))
    ids = [elem.text for elem in tree.find("IdList").findall("Id")]
    return [{"source": "pubmed", "id": f"http://identifiers.org/pubmed:{pid}", "summary": f"PubMed article {pid}"} for pid in ids]

async def pubmed_fetch(pubmed_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://togows.org/entry/pubmed/{pubmed_id}.json")
    response.raise_for_status()
    data = response.json()[0] if response.json() else {}
    return {
        "id": pubmed_id,
        "source": "pubmed",
        "label": data.get("title", ""),
        "attributes": data
    }

# --- UniProt ---
async def uniprot_search(query: str):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": query, "fields": "accession,protein_name,gene_names,organism_name", "format": "json", "size": 10}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    results = []
    for entry in data.get("results", []):
        uid = entry.get("primaryAccession")
        pname = entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "")
        results.append({
            "source": "uniprot",
            "id": f"http://purl.uniprot.org/uniprot/{uid}",
            "summary": pname
        })
    return results

async def uniprot_fetch(uniprot_id: str):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {
        "id": uniprot_id,
        "source": "uniprot",
        "label": data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", ""),
        "attributes": data
    }

# --- PubChem ---
async def pubchem_search(query: str):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query}/cids/JSON"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    ids = data.get("IdentifierList", {}).get("CID", [])
    return [{"source": "pubchem", "id": f"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID{cid}", "summary": f"Compound CID {cid}"} for cid in ids]

async def pubchem_fetch(cid: str):
    url = "https://togodx.dbcls.jp/human/sparqlist/api/metastanza_pubchem_compound"
    response = requests.get(url, params={"id": cid})
    response.raise_for_status()
    data = response.json()
    return {
        "id": cid,
        "source": "pubchem",
        "label": data.get("label", f"Compound CID {cid}"),
        "attributes": data
    }

# ======== Utility: URI → source 解決 =========
def resolve_source_from_uri(uri: str) -> str:
    if "uniprot" in uri:
        return "uniprot"
    if "pubchem" in uri or "chebi" in uri:
        return "pubchem"
    if "pubmed" in uri:
        return "pubmed"
    return "unknown"

# ======== 共通ツール =========

@server.tool()
async def search(query: str):
    """
    Search across multiple biomedical databases (PubMed, UniProt, PubChem).
    Synonym URIs are expanded using get_synonym_URIs.
    """
    results = []
    results.extend(await pubmed_search(query))
    results.extend(await uniprot_search(query))
    results.extend(await pubchem_search(query))

    for r in results:
        r["synonyms"] = get_synonym_URIs(r["id"])
    return results


@server.tool()
async def fetch(id: str):
    """
    Fetch detailed info for a given id or URI.
    Accepts any synonym (different prefix/naming scheme).

    Args: id (str): identifier or URI for whith you want to get detailed information
    Returns: JSON data whose keys are source, id, and summary
    """
    # 1. synonym展開
    synonyms = get_synonym_URIs(id)

    # 2. DB判定 & 正規化
    source, canonical = None, None
    for u in synonyms:
        src = resolve_source_from_uri(u)
        if src != "unknown":
            source, canonical = src, u
            break

    if source == "pubmed":
        return await pubmed_fetch(canonical.split(":")[-1])
    elif source == "uniprot":
        return await uniprot_fetch(canonical.split("/")[-1])
    elif source == "pubchem":
        return await pubchem_fetch(canonical.split("CID")[-1])
    else:
        raise ValueError(f"Cannot resolve source for identifier: {id}")


# ======== Entrypoint =========
if __name__ == "__main__":
    server.run(transport="sse", host="0.0.0.0", port=8800)
