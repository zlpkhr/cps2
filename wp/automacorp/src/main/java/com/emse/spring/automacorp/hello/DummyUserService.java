package com.emse.spring.automacorp.hello;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DummyUserService  implements  UserService{

    @Autowired
    GreetingService greetingService;

    @Override
    public void greetAll(List<String> names) {
        names.forEach((n)->greetingService.greet(n));
    }
}
