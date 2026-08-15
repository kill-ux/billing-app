

import pytest


# def test_create_movie(client, app_url):
#     """Test creating a new movie."""
#     movie_data = {
#         "title": "Test Movie",
#         "description": "A test movie description"
#     }
    
#     resp = client.post(f"{app_url}/api/movies", json=movie_data)
    
#     assert resp.status_code == 201
#     assert resp.json()["title"] == movie_data["title"]
#     assert resp.json()["description"] == movie_data["description"]
#     assert "id" in resp.json()
#     assert isinstance(resp.json()["id"], int)

# def test_create_movie_missing_title(client, app_url):
#     """Test creating a movie with missing required fields."""
#     movie_data = {
#         "description": "A movie without a title"
#         # Missing title
#     }
    
#     resp = client.post(f"{app_url}/api/movies", json=movie_data)
    
#     assert resp.status_code == 400
#     assert "error" in resp.json()

# def test_list_movies(client, app_url):
#     """Test listing all movies."""
#     # First ensure there's at least one movie
#     movie_data = {
#         "title": "List Test Movie",
#         "description": "A movie for listing test"
#     }
#     client.post(f"{app_url}/api/movies", json=movie_data)
    
#     resp = client.get(f"{app_url}/api/movies")
    
#     assert resp.status_code == 200
#     movies = resp.json()
#     assert len(movies) >= 1
#     assert movies[0]["title"] is not None
#     assert movies[0]["id"] is not None
#     assert "description" in movies[0]

# def test_list_movies_with_search(client, app_url):
#     """Test searching movies by title."""
#     # Create test movies
#     movies = [
#         {"title": "The Matrix", "description": "Sci-Fi classic"},
#         {"title": "Matrix Reloaded", "description": "Sequel to The Matrix"},
#         {"title": "Inception", "description": "Dream heist movie"}
#     ]
    
#     for movie in movies:
#         client.post(f"{app_url}/api/movies", json=movie)
    
#     # Search for "matrix"
#     resp = client.get(f"{app_url}/api/movies?title=matrix")
    
#     assert resp.status_code == 200
#     results = resp.json()
#     assert len(results) >= 2
#     assert all("Matrix" in movie["title"] for movie in results)

# def test_get_movie_by_id(client, app_url):
#     """Test retrieving a specific movie by ID."""
#     # Create a movie
#     movie_data = {
#         "title": "Get Movie Test",
#         "description": "A movie to retrieve by ID"
#     }
#     create_resp = client.post(f"{app_url}/api/movies", json=movie_data)
#     movie_id = create_resp.json()["id"]
    
#     # Retrieve it
#     resp = client.get(f"{app_url}/api/movies/{movie_id}")
    
#     assert resp.status_code == 200
#     assert resp.json()["id"] == movie_id
#     assert resp.json()["title"] == movie_data["title"]
#     assert resp.json()["description"] == movie_data["description"]

# def test_get_movie_not_found(client, app_url):
#     """Test retrieving a non-existent movie."""
#     resp = client.get(f"{app_url}/api/movies/99999")
    
#     assert resp.status_code == 404
#     assert "error" in resp.json()

# def test_update_movie(client, app_url):
#     """Test updating an existing movie."""
#     # Create a movie
#     create_data = {
#         "title": "Old Title",
#         "description": "Old description"
#     }
#     create_resp = client.post(f"{app_url}/api/movies", json=create_data)
#     movie_id = create_resp.json()["id"]
    
#     # Update it
#     update_data = {
#         "title": "New Title",
#         "description": "New description"
#     }
#     resp = client.put(f"{app_url}/api/movies/{movie_id}", json=update_data)
    
#     assert resp.status_code == 200
#     assert resp.json()["id"] == movie_id
#     assert resp.json()["title"] == update_data["title"]
#     assert resp.json()["description"] == update_data["description"]

# def test_update_movie_not_found(client, app_url):
#     """Test updating a non-existent movie."""
#     update_data = {
#         "title": "New Title",
#         "description": "New description"
#     }
    
#     resp = client.put(f"{app_url}/api/movies/99999", json=update_data)
    
#     assert resp.status_code == 404
#     assert "error" in resp.json()

# def test_delete_movies_all(client, app_url):
#     """Test deleting all movies."""
#     # First create some movies
#     for i in range(3):
#         movie_data = {
#             "title": f"Delete All Movie {i}",
#             "description": f"Description {i}"
#         }
#         client.post(f"{app_url}/api/movies", json=movie_data)
    
#     # Delete all
#     resp = client.delete(f"{app_url}/api/movies")
    
#     assert resp.status_code == 204
#     assert resp.text == ""
    
#     # Verify empty list
#     list_resp = client.get(f"{app_url}/api/movies")
#     assert list_resp.status_code == 200
#     assert len(list_resp.json()) == 0

# def test_delete_single_movie(client, app_url):
#     """Test deleting a specific movie."""
#     # Create a movie
#     movie_data = {
#         "title": "Movie to Delete",
#         "description": "This movie will be deleted"
#     }
#     create_resp = client.post(f"{app_url}/api/movies", json=movie_data)
#     movie_id = create_resp.json()["id"]
    
#     # Delete it
#     resp = client.delete(f"{app_url}/api/movies/{movie_id}")
    
#     assert resp.status_code == 204
#     assert resp.text == ""
    
#     # Verify it's gone
#     get_resp = client.get(f"{app_url}/api/movies/{movie_id}")
#     assert get_resp.status_code == 404

# def test_delete_movie_not_found(client, app_url):
#     """Test deleting a non-existent movie."""
#     resp = client.delete(f"{app_url}/api/movies/99999")
    
#     assert resp.status_code == 404
#     assert "error" in resp.json()


# def test_create_movie_empty_title(client, app_url):
#     """Test creating a movie with empty title."""
#     movie_data = {
#         "title": "",
#         "description": "Empty title test"
#     }
    
#     resp = client.post(f"{app_url}/api/movies", json=movie_data)
    
#     assert resp.status_code == 400
#     assert "error" in resp.json()

# # ===================== Cleanup =====================

# @pytest.fixture(scope="session", autouse=True)
# def cleanup(client, app_url):
#     """Clean up database after all tests."""
#     yield
#     try:
#         client.delete(f"{app_url}/api/movies")
#     except:
#         pass