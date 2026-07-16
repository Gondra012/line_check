import multiprocessing
import webbrowser
import time
import uvicorn

def ouvrir_navigateur():
    # Attend 2 secondes que le serveur démarre, puis ouvre la console Bureau
    time.sleep(2)
    webbrowser.open("http://localhost:8080/")

if __name__ == "__main__":
    # Évite les boucles infinies lors de la compilation
    multiprocessing.freeze_support()

    # Lance l'ouverture du navigateur dans un fil secondaire
    p = multiprocessing.Process(target=ouvrir_navigateur)
    p.start()

    # Démarre le serveur web uvicorn sur le port 8080
    uvicorn.run("main:app", host="0.0.0.0", port=8080, workers=1)
