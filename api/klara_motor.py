import google.generativeai as genai
import json
import os

# --- Konfiguration ---
# Se till att du har din API-nyckel här eller som en miljövariabel
# För enkelhetens skull, klistra in den här för detta testskript.
# Dela ALDRIG kod med en hårdkodad nyckel.
API_KEY = "AIzaSyCUVmLx0ovqSCgrYGN5DY90SGZn9thDdEU" 
genai.configure(api_key=API_KEY)

# Hjärnan i vår motor
def run_klara_engine(source_text: str, malgrupp: str, ton: str, format: str) -> str:
    """
    Kör hela Prompt Chaining-processen.
    Steg 1: Extraherar fakta från källtexten till en JSON-struktur.
    Steg 2: Använder JSON-datan för att skriva en patientvänlig text.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')

    # --- STEG 1: EXTRAHERA FAKTA ---
    print("--- Startar Steg 1: Extraherar fakta från källtext... ---")
    
    prompt_1 = f"""
    Du är en medicinsk dataanalytiker med expertis inom NLP. Din enda uppgift är att noggrant läsa den tekniska KÄLLTEXTEN nedan och extrahera information för att fylla i följande JSON-struktur. Fyll i ALLA fält. Om information för ett fält saknas i källtexten, skriv "Information saknas i källtexten". Översätt eller förenkla INTE informationen i detta steg, extrahera endast de relevanta tekniska fakta som de presenteras.

    JSON-struktur att fylla i:
    {{
      "titel": "Titel på medicin/procedur",
      "kort_forklaring": "En enda mening som förklarar vad detta är.",
      "syfte_anvandning": "Varför görs detta eller tar jag detta? Vilket problem löser det?",
      "verkningsmekanism_enkel": "Hur fungerar det i kroppen, förklarat superenkelt? (Gäller främst medicin)",
      "forberedelser": "Vad måste jag göra innan?",
      "procedur_steg_for_steg": "Vad kommer att hända under proceduren/behandlingen?",
      "efterat_effekt": "Vad händer efteråt? När mår jag bättre? Vad ska jag tänka på?",
      "viktigaste_risker_biverkningar": "Vilka är de vanligaste eller allvarligaste riskerna/biverkningarna jag bör känna till?",
      "praktisk_info": "Övrig praktisk information som tidsåtgång, bedövning etc."
    }}

    KÄLLTEXT:
    \"\"\"
    {source_text}
    \"\"\"
    """
    
    response_1 = model.generate_content(prompt_1)
    
    # Rensa upp AI-svaret så det blir ren JSON
    structured_data_text = response_1.text.replace("```json", "").replace("```", "").strip()
    print("Strukturerad data (JSON) mottagen:\n", structured_data_text)
    
    try:
        structured_data_json = json.loads(structured_data_text)
    except json.JSONDecodeError:
        print("Fel: Kunde inte tolka svaret från Steg 1 som JSON.")
        return "Ett fel uppstod vid dataextraheringen."

    # --- STEG 2: FORMULERA PATIENTTEXT ---
    print("\n--- Startar Steg 2: Formulerar patientvänlig text... ---")

    prompt_2 = f"""
    Du är "Klara", en AI-driven medicinsk copywriter. Du är expert på att skriva varma, pedagogiska och förtroendeingivande texter för patienter. Din uppgift är att använda den strukturerade JSON-DATAN nedan för att skriva en text i det specificerade FORMATET, för den valda MÅLGRUPPEN och med den önskade TONEN. Använd rubriker och korta stycken. Ignorera fält där värdet är "Information saknas i källtexten".

    PARAMETRAR:
    - MÅLGRUPP: {malgrupp}
    - TON: {ton}
    - FORMAT: {format}

    JSON-DATA:
    {json.dumps(structured_data_json, indent=2, ensure_ascii=False)}
    """

    response_2 = model.generate_content(prompt_2)
    final_text = response_2.text
    
    return final_text

# --- Exempel på hur vi kör motorn ---
if __name__ == "__main__":
    # Välj vilken källtext du vill testa (byt mellan gastroskopi_text och sertralin_text)
    gastroskopi_text = """
    Gastroskopi är en endoskopisk undersökning av matstrupe, magsäck och tolvfingertarm. Ett gastroskop, en flexibel slang med kamera och ljuskälla, förs ned via munnen. Patienten är vanligtvis sederad för att minska obehag och kväljningsreflexer. Lokalbedövande spray kan appliceras i svalget. Proceduren tar cirka 10-15 minuter. Vitalparametrar som syremättnad och puls övervakas kontinuerligt. Biopsier kan tas med en liten tång som förs in via instrumentkanalen i endoskopet för histopatologisk analys. De huvudsakliga riskerna, om än sällsynta, inkluderar perforation av esofagus eller ventrikel, blödning (särskilt efter biopsi) och aspiration. Patienten måste vara fastande i minst 6 timmar före undersökningen för att säkerställa att magsäcken är tom och för att minimera aspirationsrisken.
    """
    
    sertralin_text = """
    Sertralin är en potent och specifik hämmare av neuronalt återupptag av serotonin (5-HT) in vitro, vilket leder till en förstärkning av 5-HT:s effekter hos djur. Det har endast en mycket svag effekt på neuronalt återupptag av noradrenalin och dopamin. Vid kliniska doser blockerar sertralin upptaget av serotonin i humana trombocyter. Det saknar stimulerande, sedativa eller antikolinerga effekter samt kardiotoxicitet hos djur. I kontrollerade studier på friska försökspersoner gav sertralin ingen sedering och påverkade inte psykomotoriken. I enlighet med sin selektiva hämning av 5-HT-återupptaget ökar sertralin inte den katekolaminerga aktiviteten. Sertralin har ingen affinitet för muskarina (kolinerga), serotonerga (5HT1A, 5HT1B, 5HT2), dopaminerga, adrenerga, histaminerga eller GABA-receptorer.
    """

    # Definiera dina önskemål
    target_source_text = gastroskopi_text
    target_malgrupp = "Vuxen patient som är lite orolig"
    target_ton = "Empatisk och lugnande"
    target_format = "En FAQ för en webbsida"
    
    # Kör motorn!
    final_patient_text = run_klara_engine(target_source_text, target_malgrupp, target_ton, target_format)
    
    print("\n--- FÄRDIG PATIENTTEXT ---")
    print(final_patient_text)