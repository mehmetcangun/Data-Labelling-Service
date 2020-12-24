/*
	Users Table.
	name: 30 character most.
	surname: 30 character most.
	email: Valid, 100 character most, not null
	password: Encrpted, 1000 character most, not null
	usertype:
		- Admin | Main Duty
			- CRUD: criterias, images, domains, subdomains,
		- Labeller | Main Duty
			- Give contribution to the images
			- List images
	points: derived property
	last_seen: keeps last seen date and time
*/
create table if not exists users(
	user_id   SERIAL PRIMARY KEY,
	name      varchar(30) NOT NULL,
	surname   varchar(30) NOT NULL,
	email     varchar(100) UNIQUE NOT NULL,
	password  varchar(1000) NOT NULL,
	usertype  int NOT NULL DEFAULT 1,
	points    float NOT NULL DEFAULT 0.0,
	last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CHECK ( usertype != 1 or usertype != 0)
);

/* Prior domain's value is range 1 to 10 */
create domain prior as int
    check ( value >= 1 and value <= 10);

/*
	Domains Table.
	- name: like Animal.
    - description: about
	- priority_rate: rate 1 to 10, 10 is higher rate than 1.
	- color: hex value #FF0000 for Red
*/
create table if not exists domains(
	domain_id     SERIAL PRIMARY KEY,
	name          varchar(50) UNIQUE NOT NULL,
	description   varchar(1000) not null,
	priority_rate prior not null,
	color         varchar(6) not null
);

/*
	SubDomains Table.
	- name: like Dog or Cat
    - priority_rate: rate 1 to 10, 10 is higher rate than 1.
	- icon: icon name like 'fas fa-cat' from fontawesome
	        https://fontawesome.com/icons/cat?style=solid)

	: referenced with Domains Table to be easily categorized.
	Ex1: Animal-> Dog
	Ex2: Animal-> Cat
*/
create table if not exists subdomains(
	subdomain_id      SERIAL PRIMARY KEY,

	name              varchar(50)  NOT NULL,
	priority_rate     prior not null,
	icon              varchar(25),

	domain_id         INT NOT NULL,

	/* if the domain has subdomains,
	   the restriction is given via the subdomains of domain.
	   otherwise, the domain is deleted.
	*/
	/* Update will be need for every changes on domain */
	FOREIGN KEY(domain_id)
		REFERENCES domains(domain_id)
	    ON UPDATE CASCADE
		ON DELETE RESTRICT
);

/*
    The criterias determined with the 'criteria_selection' domain.
*/
create domain criteria_selection as float
    CHECK ( VALUE >= -5.0 and VALUE <= 5.0 );

/*
	Criteria Table.
	-> Criterias defined by Admins to evaluate contributions by image.
	- for_contribution: entry point for contribution
	- correctness: if correct, the point is added.
	- wrongness: if wrong, the point is substracted.
	- reported: if the report is done, the point is added.
	- extra_info: if the extra_info is given, the point is added.

	: Only the admins creates a criteria by referencing the User table.
*/
create table if not exists criterias(
	criteria_id      SERIAL PRIMARY KEY,
	for_contribution criteria_selection NOT NULL DEFAULT 1.0,
	correctness      criteria_selection NOT NULL DEFAULT 0.0,
	wrongness        criteria_selection NOT NULL DEFAULT 0.0,
	reported         criteria_selection NOT NULL DEFAULT 0.0,
	extra_info       criteria_selection NOT NULL DEFAULT 0.0,
	user_id         INT,
	/*
	    if the user(admin) leaves,
	    the criterias can be reassigned to another admin
	*/
	FOREIGN KEY(user_id)
		REFERENCES users(user_id)
	    ON UPDATE CASCADE
		ON DELETE SET NULL
);

create type classtype as
    enum ('Binary Classification', 'Multi-Class', 'Multi-Label');

/*
    Images table.
    - title: 250 character most, not null
    - url_path: image link, not null
    - most_contribution: maximum contribution to be given by user like attempts
    - classification_type: the type only have
      'Binary Classification', 'Multi-Class' and 'Multi-Label'

    : created by user(admin) by using user_id reference from Users table.
    : image have criteria for evaluation
      by using criteria_id reference from Criteria Table.
*/
create table if not exists images(
	images_id             SERIAL PRIMARY KEY,

	title                 varchar(250) NOT NULL,
	url_path              varchar(250) NOT NULL,
	most_contribution     int,
	classification_type   classtype,

	user_id               INT,
	criteria_id           INT NOT NULL,
	/*
	   if the user(admin) leaves,
	   the images can be reassigned to another admin
	*/
	FOREIGN KEY(user_id)
		REFERENCES users(user_id)
	    ON UPDATE CASCADE
		ON DELETE SET NULL,
	/* if the image has criteria, the delete operation is restricted */
	/* otherwise, the criteria is deleted. */
	FOREIGN KEY(criteria_id)
		REFERENCES criterias(criteria_id)
		ON UPDATE CASCADE
	    ON DELETE RESTRICT,
	CHECK ( most_contribution >= 1 )
);

/*
    Labels table.
    - is_correct: keeps the correct or incorrect status for image

    : Many images can be part of many subdomains.
 */
create table if not exists labels(
	label_id      SERIAL PRIMARY KEY,

	is_correct    BOOLEAN NOT NULL DEFAULT FALSE,

	subdomain_id  INT NOT NULL,
	images_id     INT NOT NULL,

	/* if the label has subdomain, the delete operation is restricted. */
	/* otherwise, the subdomain is deleted. */
	FOREIGN KEY(subdomain_id)
		REFERENCES subdomains(subdomain_id)
	    ON UPDATE CASCADE
		ON DELETE RESTRICT,

	/* if the image is deleted, the labels are not necessary anymore. */
	FOREIGN KEY(images_id)
		REFERENCES images(images_id)
		ON UPDATE CASCADE
	    ON DELETE CASCADE
);

/* reports type is used in contributions table. */
create type reports as enum ('blur image', 'no image', 'no correct answer');

/*
    Contributions table.
    - label_id: provides to access image and its subdomains
    - reported: enum type, only can be reports' type values or NULL.
    - extra_info: the details about image when contribution is done by labeller.

    : Contribution determined with labels providing image and its subdomains.
    : Labeller contributes to images so the contribution is related to user.
*/
create table if not exists contributions(
	contribution_id SERIAL PRIMARY KEY,

	label_id        int NOT NULL,
	reported        reports,
	extra_info      varchar(1500),

	user_id         int,

	/* if the label is deleted, there is no need this contribution. */
	FOREIGN KEY(label_id)
		REFERENCES labels(label_id)
	    ON UPDATE CASCADE
		ON DELETE CASCADE,

	/*
	   if the user(labeller) is deleted,
	   the contribution status is also important for statistics.
	*/
	FOREIGN KEY(user_id)
		REFERENCES users(user_id)
	    ON UPDATE CASCADE
		ON DELETE SET NULL
);
