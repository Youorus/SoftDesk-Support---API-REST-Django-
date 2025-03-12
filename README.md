# SoftDesk Support - API RESTful

![Django](https://img.shields.io/badge/Django-4.2.20-green)
![DRF](https://img.shields.io/badge/DRF-3.14.0-blue)
![JWT](https://img.shields.io/badge/JWT-5.2.2-orange)

**SoftDesk Support** est une API RESTful développée avec Django et Django REST Framework (DRF) pour la gestion de projets, d'issues (problèmes), de commentaires et d'utilisateurs. Cette API permet aux utilisateurs de collaborer sur des projets en créant des issues, en les assignant à des contributeurs, et en ajoutant des commentaires pour faciliter la communication.

![](softDesk-image.png)

---

## Fonctionnalités principales

- **Gestion des utilisateurs** :
  - Inscription et authentification via JWT (JSON Web Tokens).
  - Respect des normes RGPD : âge minimum de 15 ans et gestion des consentements (`can_be_contacted`, `can_data_be_shared`).

- **Gestion des projets** :
  - Création, lecture, mise à jour et suppression de projets.
  - Attribution de contributeurs à un projet.
  - Accès restreint aux contributeurs du projet.

- **Gestion des issues (problèmes)** :
  - Création d'issues avec des priorités (`LOW`, `MEDIUM`, `HIGH`), des balises (`BUG`, `FEATURE`, `TASK`) et des statuts (`To Do`, `In Progress`, `Finished`).
  - Assignation d'issues à des contributeurs.

- **Gestion des commentaires** :
  - Ajout de commentaires sur les issues pour faciliter la communication.
  - Horodatage automatique des commentaires.

- **Pagination** :
  - Pagination des listes de ressources (projets, issues, commentaires).

---

## Ressources de l'API

### 1. **Utilisateurs (`User`)**
- **Champs** : `id` (UUID), `username`, `password`, `age`, `can_be_contacted`, `can_data_be_shared`, `created_at`.
- **Endpoints** :
  - `POST /register/` : Inscription d'un nouvel utilisateur.
  - `POST /token/` : Authentification et obtention d'un JWT.
  - `GET /users/` : Liste des utilisateurs (admin seulement).
  - `GET /users/{id}/` : Détails d'un utilisateur.
  - `PUT/PATCH /users/{id}/` : Mise à jour d'un utilisateur.
  - `DELETE /users/{id}/` : Suppression d'un utilisateur.

### 2. **Projets (`Project`)**
- **Champs** : `id`, `name`, `description`, `type` (`backend`, `frontend`, `ios`, `android`), `author`, `contributors`, `created_at`.
- **Endpoints** :
  - `GET /projects/` : Liste des projets accessibles.
  - `POST /projects/` : Création d'un nouveau projet.
  - `GET /projects/{id}/` : Détails d'un projet.
  - `PUT/PATCH /projects/{id}/` : Mise à jour d'un projet.
  - `DELETE /projects/{id}/` : Suppression d'un projet.
  - `GET /projects/{id}/contributors/` : Liste des contributeurs d'un projet.
  - `POST /projects/{id}/contributors/` : Ajout d'un contributeur à un projet.
  - `DELETE /projects/{id}/contributors/{user_id}/` : Suppression d'un contributeur.

### 3. **Issues (`Issue`)**
- **Champs** : `id`, `title`, `description`, `priority` (`LOW`, `MEDIUM`, `HIGH`), `tag` (`BUG`, `FEATURE`, `TASK`), `status` (`To Do`, `In Progress`, `Finished`), `assignee`, `project`, `author`, `created_at`.
- **Endpoints** :
  - `GET /projects/{project_id}/issues/` : Liste des issues d'un projet.
  - `POST /projects/{project_id}/issues/` : Création d'une issue.
  - `GET /projects/{project_id}/issues/{issue_id}/` : Détails d'une issue.
  - `PUT/PATCH /projects/{project_id}/issues/{issue_id}/` : Mise à jour d'une issue.
  - `DELETE /projects/{project_id}/issues/{issue_id}/` : Suppression d'une issue.

### 4. **Commentaires (`Comment`)**
- **Champs** : `id`, `content`, `issue`, `author`, `created_at`.
- **Endpoints** :
  - `GET /issues/{issue_id}/comments/` : Liste des commentaires d'une issue.
  - `POST /issues/{issue_id}/comments/` : Création d'un commentaire.
  - `GET /issues/{issue_id}/comments/{comment_id}/` : Détails d'un commentaire.
  - `PUT/PATCH /issues/{issue_id}/comments/{comment_id}/` : Mise à jour d'un commentaire.
  - `DELETE /issues/{issue_id}/comments/{comment_id}/` : Suppression d'un commentaire.

---

## Installation et configuration

### Prérequis
- Python 3.9 ou supérieur
- Pip (gestionnaire de paquets Python)
- PostgreSQL (ou tout autre SGBD supporté par Django)

### Étapes d'installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/Youorus/SoftDesk-Support---API-REST-Django-
   cd softdesk-support
   
# Installation et Configuration du Projet

## Prérequis

Avant de commencer, assurez-vous d'avoir installé Python sur votre machine. Si ce n'est pas déjà fait, vous pouvez télécharger Python ici : https://www.python.org/downloads/

## 1. Créer un environnement virtuel

Pour créer un environnement virtuel, exécutez la commande suivante dans le terminal :

```bash
python -m venv venv
```

Ensuite, activez l'environnement virtuel :

- **Sur macOS/Linux :**

  ```bash
  source venv/bin/activate
  ```

- **Sur Windows :**

  ```bash
  venv\Scripts\activate
  ```

## 2. Installer les dépendances

Une fois l'environnement virtuel activé, installez toutes les dépendances nécessaires au projet en exécutant la commande suivante :

```bash
pip install -r requirements.txt
```

Cela va installer toutes les bibliothèques nécessaires listées dans le fichier `requirements.txt`.

## 3. Appliquer les migrations

Appliquez les migrations pour configurer la base de données en exécutant la commande suivante :

```bash
python manage.py migrate
```

Cela créera les tables et la structure nécessaire dans votre base de données.

## 4. Lancer le serveur de développement

Pour lancer le serveur de développement de Django, utilisez la commande suivante :

```bash
python manage.py runserver
```

Le serveur sera disponible à l'adresse suivante : [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## 5. Accéder à l'API

Une fois le serveur en marche, vous pourrez accéder à l'API à l'adresse suivante : 

[http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Auteurs

- Marc
- Supervision Openclassrooms
