.PHONY: seed seed-users seed-stories

seed:
	python -m seeds.run_all

seed-users:
	python -m seeds.seed_users

seed-stories:
	python -m seeds.seed_stories
