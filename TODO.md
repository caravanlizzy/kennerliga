# Frontend
### Forms
- Create new Game
    - with nested create gameOption
- Post a game result
- edit profile
- post feedback

### Pages
- for users
  - Landing page with result overviews
  - Current season overview
  - My leagues with current league at the top, past leagues below
- for admins
  - manage users (usersList already exists, no actions possible)
  - manage announcements
  - manage games (GamesList)

## Backend

### User Management
- Send an account invitation mail with a link where user can register

### Permissions
- Add permissions to all the REST routes
    - i.e. who can create a match result
    - allow game creation, user ceration etc for admins only

### Automated
- Create a service/job that generates the new leagues 1 week before each season, opens the season, sends notifications 
- generate leagues at the beginning of a season
### GameSelection
- At the start of a season people select their games and after all games have been added, people can ban games.
    - model to persist selections
    - logic to catch bans and apply accordingly