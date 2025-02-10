import os

def read_file_content(file_path):
    """Lit le contenu d'un fichier et le retourne."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"**Erreur lors de la lecture du fichier :** {e}"

def generate_prompt(project_root, output_file):
    prompt_lines = []
    prompt_lines.append("### Structure du Projet\n")
    prompt_lines.append(f"Voici la structure actuelle du projet situé dans `{project_root}` :\n")

    for root, dirs, files in os.walk(project_root):
        # Calculer le niveau d'indentation basé sur la profondeur du dossier
        level = root.replace(project_root, '').count(os.sep)
        indent = '    ' * level
        folder_name = os.path.basename(root)
        if folder_name == '':
            folder_name = os.path.basename(project_root)
        prompt_lines.append(f"{indent}{folder_name}/")
        sub_indent = '    ' * (level + 1)
        for file in files:
            prompt_lines.append(f"{sub_indent}├── {file}")

    prompt_lines.append("\n### Description des Composants Principaux\n")

    # Décrire les dossiers principaux
    static_dir = os.path.join(project_root, 'static')
    if os.path.isdir(static_dir):
        prompt_lines.append("\n- **static/** : Contient les fichiers statiques tels que les images, les feuilles de style CSS, et les scripts JavaScript.")
        for file in os.listdir(static_dir):
            if os.path.isfile(os.path.join(static_dir, file)):
                prompt_lines.append(f"    - `{file}` : Description du fichier `{file}`.")

    templates_dir = os.path.join(project_root, 'templates')
    if os.path.isdir(templates_dir):
        prompt_lines.append("\n- **templates/** : Contient les fichiers de templates HTML utilisés par le serveur web.")
        for template_file in os.listdir(templates_dir):
            if os.path.isfile(os.path.join(templates_dir, template_file)):
                prompt_lines.append(f"    - `{template_file}` : Template pour la page `{template_file.replace('.html','')}`.")

    # Décrire et inclure le contenu des fichiers principaux
    app_py = os.path.join(project_root, 'app.py')
    if os.path.isfile(app_py):
        prompt_lines.append("\n- **app.py** : Fichier principal de l'application contenant le code backend (probablement une application Flask ou similaire).")
        app_py_content = read_file_content(app_py)
        prompt_lines.append("    ```python")
        prompt_lines.append(app_py_content)
        prompt_lines.append("    ```")

    requirements = os.path.join(project_root, 'requirements.txt')
    if os.path.isfile(requirements):
        prompt_lines.append("- **requirements.txt** : Liste des dépendances Python nécessaires à l'application.")
        requirements_content = read_file_content(requirements)
        prompt_lines.append("    ```plaintext")
        prompt_lines.append(requirements_content)
        prompt_lines.append("    ```")

    dockerfile = os.path.join(project_root, 'Dockerfile')
    if os.path.isfile(dockerfile):
        prompt_lines.append("- **Dockerfile** : Fichier de configuration pour la création de l'image Docker de l'application.")
        dockerfile_content = read_file_content(dockerfile)
        prompt_lines.append("    ```dockerfile")
        prompt_lines.append(dockerfile_content)
        prompt_lines.append("    ```")

    docker_compose = os.path.join(project_root, 'docker-compose.yml')
    if os.path.isfile(docker_compose):
        prompt_lines.append("- **docker-compose.yml** : Configuration Docker Compose pour orchestrer les conteneurs de l'application.")
        docker_compose_content = read_file_content(docker_compose)
        prompt_lines.append("    ```yaml")
        prompt_lines.append(docker_compose_content)
        prompt_lines.append("    ```")

    env_file = os.path.join(project_root, '.env')
    if os.path.isfile(env_file):
        prompt_lines.append("- **.env** : Fichier contenant les variables d'environnement nécessaires à l'application.")
        env_content = read_file_content(env_file)
        prompt_lines.append("    ```env")
        prompt_lines.append(env_content)
        prompt_lines.append("    ```")

    # Inclure le contenu des fichiers de templates
    if os.path.isdir(templates_dir):
        for template_file in os.listdir(templates_dir):
            template_path = os.path.join(templates_dir, template_file)
            if os.path.isfile(template_path):
                prompt_lines.append(f"\n#### Contenu de `{template_file}`")
                template_content = read_file_content(template_path)
                # Définir le langage pour le formatage, généralement HTML
                prompt_lines.append("```html")
                prompt_lines.append(template_content)
                prompt_lines.append("```")

    # Écrire le prompt dans le fichier de sortie
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(prompt_lines))

    print(f"Le fichier de prompt a été généré avec succès : {output_file}")

if __name__ == "__main__":
    # Définissez le chemin racine de votre projet
    projet_racine = 'app'  # Modifier si nécessaire

    # Définissez le nom du fichier de sortie
    fichier_sortie = 'prompt_projet.md'

    generate_prompt(projet_racine, fichier_sortie)