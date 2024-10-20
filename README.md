# Budget manager

Users may follow their spending habbits, create budgets and view their assets. The goal of this project is to be a virtual checkbook.

### This application or it's author WILL NOT
- use the information against the users, for example to advertise to them or sell the data to any advertisers.
- control users' assets.
- manage the finances for the user.
- provide any kind of financial guidance for the users.

## Features
- [x] Graphs.
  - [x] Asset value graphs.
  - [ ] Spendings graphs.
  - [ ] ~~Projected value graphs.~~
- [x] Users may add their receipts to the system.
  - [x] Each receipt can be broken down line-by-line, product-by-product.
    - [x] Each line item may be individually added or removed.
  - [ ] ~~Each line item may have their sales and one-off markdowns added for more insights.~~
  - [ ] ~~Each line item may be linked to another when comparing vendors.~~
  - [x] Users may delete their receipts.
- [x] Users may add assets and keep track of them.
  - [x] Users may view their assets and add new ones as they wish.
    - [x] Each asset has it's own history associated with it.
      - [x] Users may view and interact with said history.
  - [x] Users may delete their assets and the associated history.
- [ ] ~~Users may create groups.~~
  - [ ] ~~Users may review expenses in their own groups.~~
  - [ ] ~~Users may add expenses in their own groups (depending on their rights in the group).~~
  - [ ] ~~Users may mark their contributions towards expenses in their own groups.~~
  - [ ] ~~Users may create one-off groups for event and such.~~
- [ ] Users may adjust their interface preferences.

## Setup guide

1. Install dependencies `pip install -r requirements.txt`.
2. Create a database using `postgresql`.
3. Add keys `DATABASE_URI` and `SECRET_KEY` to a `.env` -file in the root.
4. Add database tables using `psql < schema.sql`
5. Run the app using `flask --app src/main.py run`
6. Add test user by visiting link `http://localhost/api/test/user`.
7. Login with username `test` and password `test`. (You can see an error message if you try to login before the user is created.)
