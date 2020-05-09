import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}



def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass




def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    
    Compute the shortest path between the two people, and prints out the path.
    Returns: (movie_id,person_id)
    
    Breadth First Search (BFS):
    
    1. BFS looks at a shallower nodes first
    2. BFS looks at all the nodes that are one away from the initial state
    3. Then it will explore nodes that are two away, three away..(BFS takes the option of exploring all the possible paths kind of at the same time bouncing back between them, looking deeper and deeper at each one making sure that the shallower ones or the ones that are closer to the initial state earlier.
    4. It will keep comparing until we reach our goal.


    Specifications:
    1. Function should return a list where each item is (movie_id,person_id) pair in the 
       path from the source to the target
       
    2. If no possible path, returns None.
    
    3. 'neighbors_for_person' function
       Input: Person's Id
       Output: a set of (movie_id,person_id) pairs for all people who starred in a movie 
               with a given person.
               
    #Pseudocode for BFS 
      
        create a queue Q 
        mark v as visited and put v into Q 
        while Q is non-empty 
        remove the head u of Q 
        mark and enqueue all (unvisited) neighbours of u
        
        
    The algorithm works as follows:

    1. Start by putting any one of the graph's vertices at the back of a queue.
    2. Take the front item of the queue and add it to the visited list.
    3. Create a list of that vertex's adjacent nodes. Add the ones which aren't in the visited list to the back of the queue.
    4. Keep repeating steps 2 and 3 until the queue is empty.
    
    
    The Chain:
    
        The Source is in Movie A with Person B
        The Person B is in Movie B with Person C
        The Person C is in Movie C with Target

   
    """
    #Start represents the initial state. This is the starting point. 
    start = Node(state = source, parent = None, action = None)
    
    frontier = QueueFrontier()
    
    #We start with a frontier that has the initial state of our agent which is 'start'
    frontier.add(start)
    
    #We create an explored set which is empty
    explored = set()
    
    #While Loop runs until the condition because False
    while True:
        #If the frontier is empty, then return none
        if frontier.empty():
            return None
        
        #remove the node from the frontier
        node = frontier.remove()
        
        #add it to the explored set
        explored.add(node.state)
        
        #expand node and add the resulting node to the frontier, if they aren't already in the frontier and in the explored set
        neighbours = neighbors_for_person(node.state)
        
        for movie , actor in neighbours:
            if actor not in explored and not frontier.contains_state(actor):
                child = Node(state = actor, parent = node, action = movie)
                if child.state == target:
                    path = []
                    node = child
                    while node.parent is not None:
                        path.append(( node.action, node.state ))
                        node = node.parent
                    path.reverse()
                    return path
                frontier.add(child)
    
    raise NotImplementedError


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    
    Retrieves IMDB id for a person's name
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()









