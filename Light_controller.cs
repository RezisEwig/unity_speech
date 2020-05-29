using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Light_controller : MonoBehaviour
{
    [SerializeField] GameObject kitchen;
    [SerializeField] GameObject living_room;
    [SerializeField] GameObject guest_room;
    [SerializeField] GameObject my_room;
    [SerializeField] GameObject bedroom;
    [SerializeField] GameObject washroom;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Alpha1))
            {
            kitchen.SetActive(true);
        }

        if (Input.GetKeyDown(KeyCode.Q))
        {
            kitchen.SetActive(false);
        }

        if (Input.GetKeyDown(KeyCode.Alpha2))
        {
            living_room.SetActive(true);
        }

        if (Input.GetKeyDown(KeyCode.W))
        {
            living_room.SetActive(false);
        }

        if (Input.GetKeyDown(KeyCode.Alpha3))
        {
            guest_room.SetActive(true);
        }

        if (Input.GetKeyDown(KeyCode.E))
        {
            guest_room.SetActive(false);
        }

        if (Input.GetKeyDown(KeyCode.Alpha4))
        {
            my_room.SetActive(true);
        }

        if (Input.GetKeyDown(KeyCode.R))
        {
            my_room.SetActive(false);
        }

        if (Input.GetKeyDown(KeyCode.Alpha5))
        {
            bedroom.SetActive(true);
        }

        if (Input.GetKeyDown(KeyCode.T))
        {
            bedroom.SetActive(false);
        }

        if (Input.GetKeyDown(KeyCode.Alpha6))
        {
            washroom.SetActive(true);
        }

        if (Input.GetKeyDown(KeyCode.Y))
        {
            washroom.SetActive(false);
        }


    }
}
