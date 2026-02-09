"""Epic-related tools for Plane MCP Server."""
from typing import get_args

from fastmcp import FastMCP
from plane.models.enums import PriorityEnum
from plane.models.epics import Epic, PaginatedEpicResponse
from plane.models.query_params import PaginatedQueryParams, RetrieveQueryParams
from plane.models.work_items import (
    CreateWorkItem,
    UpdateWorkItem,
    WorkItem,
)

from plane_mcp.client import get_plane_client_context


def register_epic_tools(mcp: FastMCP) -> None:
    """Register all epic-related tools with the MCP server."""

    def _get_epic_work_item_type_id() -> str | None:
        """Helper function to get the work item type ID for epics."""
        client, workspace_slug = get_plane_client_context()
        response = client.work_item_types.list(workspace_slug=workspace_slug, project_id="")

        for work_item_type in response:
            if work_item_type.is_epic:
                return work_item_type.id

        return None

    @mcp.tool()
    def list_epics(
        project_id: str,
        cursor: str | None = None,
        per_page: int | None = None,
    ) -> list[Epic]:
        """
        List all epics in a project.

        Args:
            workspace_slug: The workspace slug identifier
            project_id: UUID of the project
            cursor: Pagination cursor for getting next set of results
            per_page: Number of results per page (1-100)
            expand: Comma-separated list of related fields to expand in response
            fields: Comma-separated list of fields to include in response
            order_by: Field to order results by. Prefix with '-' for descending order
            external_id: External system identifier for filtering or lookup
            external_source: External system source name for filtering or lookup

        Returns:
            List of WorkItem objects
        """
        client, workspace_slug = get_plane_client_context()

        params = PaginatedQueryParams(
            cursor=cursor,
            per_page=per_page,
        )

        response: PaginatedEpicResponse = client.epics.list(
            workspace_slug=workspace_slug,
            project_id=project_id,
            params=params,
        )

        return response.results
    

    @mcp.tool()
    def create_epic(
        project_id: str,
        name: str,
        assignees: list[str] | None = None,
        labels: list[str] | None = None,
        point: int | None = None,
        description_html: str | None = None,
        description_stripped: str | None = None,
        priority: str | None = None,
        start_date: str | None = None,
        target_date: str | None = None,
        sort_order: float | None = None,
        is_draft: bool | None = None,
        external_source: str | None = None,
        external_id: str | None = None,
        state: str | None = None,
        estimate_point: str | None = None,
    ) -> Epic:
        """
        Create a new epic.

        Args:
            workspace_slug: The workspace slug identifier
            project_id: UUID of the project
            name: Epic name (required)
            assignees: List of user IDs to assign to the epic
            labels: List of label IDs to attach to the epic
            point: Story point value
            description_html: HTML description of the epic
            description_stripped: Plain text description (stripped of HTML)
            priority: Priority level (urgent, high, medium, low, none)
            start_date: Start date (ISO 8601 format)
            target_date: Target/end date (ISO 8601 format)
            sort_order: Sort order value
            is_draft: Whether the work item is a draft
            external_source: External system source name
            external_id: External system identifier
            state: UUID of the state
            estimate_point: Estimate point value

        Returns:
            Created WorkItem object
        """
        work_item_type_id = _get_epic_work_item_type_id()

        client, workspace_slug = get_plane_client_context()

        # Validate priority against allowed literal values
        validated_priority: PriorityEnum | None = (
            priority if priority in get_args(PriorityEnum) else None  # type: ignore[assignment]
        )

        data = CreateWorkItem(
            name=name,
            assignees=assignees,
            labels=labels,
            type_id=work_item_type_id,
            point=point,
            description_html=description_html,
            description_stripped=description_stripped,
            priority=validated_priority,
            start_date=start_date,
            target_date=target_date,
            sort_order=sort_order,
            is_draft=is_draft,
            external_source=external_source,
            external_id=external_id,
            state=state,
            estimate_point=estimate_point,
        )

        work_item = client.work_items.create(
            workspace_slug=workspace_slug, project_id=project_id, data=data
        )

        return client.epics.retrieve(
            workspace_slug=workspace_slug,
            project_id=project_id,
            epic_id=work_item.id,
        )
    
    @mcp.tool()
    def update_epic(
        project_id: str,
        epic_id: str,
        name: str | None = None,
        assignees: list[str] | None = None,
        labels: list[str] | None = None,
        point: int | None = None,
        description_html: str | None = None,
        description_stripped: str | None = None,
        priority: str | None = None,
        start_date: str | None = None,
        target_date: str | None = None,
        sort_order: float | None = None,
        is_draft: bool | None = None,
        external_source: str | None = None,
        external_id: str | None = None,
        state: str | None = None,
        estimate_point: str | None = None,
    ) -> WorkItem:
        """
        Update an epic by ID.

        Args:
            workspace_slug: The workspace slug identifier
            project_id: UUID of the project
            epic_id: UUID of the epic
            name: Epic name
            assignees: List of user IDs to assign to the epic
            labels: List of label IDs to attach to the epic
            point: Story point value
            description_html: HTML description of the epic
            description_stripped: Plain text description (stripped of HTML)
            priority: Priority level (urgent, high, medium, low, none)
            start_date: Start date (ISO 8601 format)
            target_date: Target/end date (ISO 8601 format)
            sort_order: Sort order value
            is_draft: Whether the work item is a draft
            external_source: External system source name
            external_id: External system identifier
            state: UUID of the state
            estimate_point: Estimate point value

        Returns:
            Updated WorkItem object
        """
        client, workspace_slug = get_plane_client_context()

        # Validate priority against allowed literal values
        validated_priority: PriorityEnum | None = (
            priority if priority in get_args(PriorityEnum) else None  # type: ignore[assignment]
        )

        data = UpdateWorkItem(
            name=name,
            assignees=assignees,
            labels=labels,
            point=point,
            description_html=description_html,
            description_stripped=description_stripped,
            priority=validated_priority,
            start_date=start_date,
            target_date=target_date,
            sort_order=sort_order,
            is_draft=is_draft,
            external_source=external_source,
            external_id=external_id,
            state=state,
            estimate_point=estimate_point
        )

        work_item = client.work_items.update(
            workspace_slug=workspace_slug,
            project_id=project_id,
            work_item_id=epic_id,
            data=data,
        )

        return client.epics.retrieve(
            workspace_slug=workspace_slug,
            project_id=project_id,
            epic_id=work_item.id,
        )   

    @mcp.tool()
    def retrieve_epic(
        project_id: str,
        epic_id: str,        
    ) -> Epic:
        """
        Retrieve a epic by ID.

        Args:
            workspace_slug: The workspace slug identifier
            project_id: UUID of the project
            epic_id: UUID of the epic

        Returns:
            Epic object
        """
        client, workspace_slug = get_plane_client_context()

        params = RetrieveQueryParams()

        return client.epics.retrieve(
            workspace_slug=workspace_slug,
            project_id=project_id,
            epic_id=epic_id,
            params=params,
        )
    
    @mcp.tool()
    def delete_epic(
        project_id: str,
        epic_id: str,        
    ) -> None:
        """
        Delete a epic by ID.

        Args:
            workspace_slug: The workspace slug identifier
            project_id: UUID of the project
            epic_id: UUID of the epic

        Returns:
            None
        """
        client, workspace_slug = get_plane_client_context()

        return client.work_items.delete(
            workspace_slug=workspace_slug,
            project_id=project_id,
            work_item_id=epic_id,
        )
