from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Optional, List

class Person(BaseModel):
    name: str
    age: int
    city: str
    isAdult: Optional[bool] = True
    
person1 = Person(name="Sneha", age=35, city="Indore")

print(person1)

@dataclass
class Person2():
    name: str
    age: int
    city: str
    
person2 = Person2(name="Sneha", age=23, city=23)
print(person2)

class Classroom(BaseModel):
    room_number: str
    students: List[str]
    capacity: Optional[int] = 40
    
class1 = Classroom(room_number="1", students=["Amy","Emma","Ben","Ross"],capacity=4)
print(class1)
class2 = Classroom(room_number="1", students=("Amy","Emma","Ben","Ross"),capacity=4)
print(class2.students)

try:
    invalid_val = Classroom(room_number="1", students=["Sneha",123], capacity=20)
    print(invalid_val)
except ValueError as e:
    print(e)

# Nested Models

class Address(BaseModel):
    street : str
    city: str
    zip_code : str
    
class Customer(BaseModel):
    cus_id: str
    name: str
    address: Address
    
customer = Customer(cus_id="123", name="sneha", address={"street" : "street 123" , "city" : "Indore", "zip_code": "452010"}  )
print(customer)

class Item(BaseModel):
    name: str=Field(min_length=2, max_length=1000)
    amount: float=Field(gt=0,le=1000)
    quantity: int=Field(ge=0, le=10)
    
item1 = Item(name="chair", amount=24, quantity=6)
print(item1)

try: 
    item2 = Item(name="s", amount=-1, quantity=2)
    print(item2)
except ValueError as e:
    print(e)
    
class User(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    age: int = Field(default=18, description="User age defaults to 18", gt=0, lt=110)
    email: str = Field(default_factory=lambda: "user@example.com", description="Default email address")
    
user1 = User(username="alice")
print(user1)
    
user2 = User(username="bob", age=25, email="bob@domain.com")
print(user2)

print(User.model_json_schema())