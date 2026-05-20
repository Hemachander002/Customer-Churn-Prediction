def get_requirements(file_path) -> list[str]:
    with open(file_path, 'r') as file:
        requirements = file.read().splitlines()
    return requirements

li = get_requirements("requirements.txt")
print(li)