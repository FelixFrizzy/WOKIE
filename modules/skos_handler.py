# skos_handler.py
import rdflib

SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")

# constants for relevant SKOS vocabulary properties
SKOS_VOCABULARY_PROPERTIES = {
    "dctdescription": rdflib.URIRef("http://purl.org/dc/terms/description"),
    "dcdescription": rdflib.URIRef("http://purl.org/dc/elements/1.1/description")
}

# constants for relevant SKOS term properties
SKOS_TERM_PROPERTIES = {
    "prefLabel": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
    "altLabel": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#altLabel"),
    "note": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#note"),
    "scopeNote": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#scopeNote"),
    "definition": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#definition"),
    "example": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#example"),
    "closeMatch": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#closeMatch"),
    "exactMatch": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#exactMatch"),
    "relatedMatch": rdflib.URIRef("http://www.w3.org/2004/02/skos/core#relatedMatch")
}

def load_graph(input_file):
    """
    Loads the SKOS file and returns the RDF graph along with its format.
    """
    g = rdflib.Graph()
    fileformat = rdflib.util.guess_format(input_file)
    if fileformat is None:
        raise ValueError(f"Could not guess file format for file: {input_file}")
    g.parse(input_file, format=fileformat)
    return g, fileformat

def extract_vocabulary_context(graph):
    """
    Extracts vocabulary-level context (=general vocabulary decription) from the ConceptScheme.
    """
    #TODO check where voc level description is usually stored
    vocab_context = None
    concept_scheme = next(graph.subjects(rdflib.RDF.type, SKOS.ConceptScheme), None)
    if concept_scheme:
        # Try dcterms:description first.
        for desc in graph.objects(concept_scheme, SKOS_VOCABULARY_PROPERTIES["dctdescription"]):
            if str(desc).strip():
                vocab_context = str(desc).strip()
                break
        # Fallback to dc:description.
        if not vocab_context:
            for desc in graph.objects(concept_scheme, SKOS_VOCABULARY_PROPERTIES["dcdescription"]):
                if str(desc).strip():
                    vocab_context = str(desc).strip()
                    break
    return vocab_context

def extract_term_properties(graph):
    """
    Extracts a dictionary of term properties for each SKOS Concept in the graph.
    
    Returns a dictionary in the following structure:
      { concept: { property_name: { language: [list of literals] }, ... }, ... }
    """
    term_props = {}
    for concept in graph.subjects(rdflib.RDF.type, SKOS.Concept):
        term_props[concept] = {}
        for prop_name, prop_uri in SKOS_TERM_PROPERTIES.items():
            for obj in graph.objects(concept, prop_uri):
                # Only consider literal values.
                if not isinstance(obj, rdflib.Literal):
                    continue
                lang = obj.language if obj.language else "none"
                if prop_name not in term_props[concept]:
                    term_props[concept][prop_name] = {}
                if lang not in term_props[concept][prop_name]:
                    term_props[concept][prop_name][lang] = []
                term_props[concept][prop_name][lang].append(obj)
    return term_props
